/*  Do those Ceremonies! */

#include "config.h"
#include "constant.h"
#include "types.h"
#include "externs.h"

void speak()
{
   int i, j, item_val, dir, inst_power;
  int choice, chance, result;
  register struct flags *f_ptr;
  register struct misc *p_ptr;
  register inven_type *i_ptr;
  register spell_type *m_ptr;
#ifdef ATARIST_MWC
  int32u holder;
#endif

  free_turn_flag = TRUE;
  if (class[py.misc.pclass].spell != SAGE)
    msg_print("You don't know any ceremonies.");
  else if (py.flags.blind > 0)
    msg_print("You can't see to read your book!");
  else if (no_light())
    msg_print("You have no light to read by.");
  else if (py.flags.confused > 0)
    msg_print("You are too confused.");
  else if (!find_range(TV_SAGE_BOOK, TV_NEVER, &i, &j))
    msg_print("But you are not carrying any spell books!");
  else if (get_item(&item_val, "Use which spell book?", i, j, CNIL, CNIL))
    {
     result = cast_spell("Perform which ceremony?", item_val, &choice, &chance);
     if (result<0)
      msg_print("You don't know any ceremonies from that book!");
     else if (result > 0)
       {
        m_ptr = &magic_spell[py.misc.pclass-1][choice];
        free_turn_flag=FALSE;
        if (randint(100) < chance)
         msg_print("You didn't perform the ceremony correctly!");
        else
	  {
           switch(choice+1)
	     {
	    case 1:
              (void) detect_evil();
              break;
	    case 2:
              (void) detect_monsters();
              break;
            case 3:
             (void) hp_player(damroll(3,4));
             (void) slow_poison();
              break;
            case 4:
              (void) light_area(char_row, char_col);
              break;
            case 5:
              if (get_dir(CNIL, &dir))
               fire_bolt(GF_MAGIC_MISSILE, dir, char_row, char_col,
                damroll(3,4),"white thread");
              break;   
            case 6: 
              (void) detect_sdoor();
              (void) detect_trap();
              break;
            case 7:
              if (!py.flags.word_recall)
               msg_print("The air around you becomes charged.");
              py.flags.word_recall+=10+randint(20);
              break;
            case 8:
              (void) detect_treasure();
              break;
            case 9:
              if (get_dir(CNIL, &dir))
               (void) light_line(dir, char_row, char_col);
              break;
            case 10:
              (void) recharge(50);
              break;
	    case 11:
              (void) detect_invisible();
              break;
            case 12:
               (void) teleport(py.misc.lev*7/2);
               break;
            case 13:
               (void) map_area();
               (void) detect_object();
               break;
            case 14:
               py.flags.see_inv += 30 + randint(py.misc.lev);
               py.flags.tim_infra += 30 + randint(py.misc.lev);
               break;
            case 15:
              (void) ident_spell();
              break;
	    case 16:
              if (get_dir(CNIL, &dir))
               fire_ball(GF_MAGIC_MISSILE, dir, char_row, char_col,
                damroll(4,9), "Gold Sphere");
              break;
            case 17:
              (void) hp_player(6,7);
              (void) cure_poison();
              break;
	    case 18:
             (void) create_food();
             break;
            case 19:
              if (get_dir(CNIL, &dir))
               fire_ball(GF_LIGHTNING, dir, char_row, char_col,
                12+damroll(4,6),"Blinding Sphere");                
              break;
            case 20:
              sleep_monsters2();
              break;
	    case 21:
              (void) speed_monsters(-1);
              break;
	    case 22:
              (void) mass_poly();
              break;
	    case 23:
              py.flags.resist_cold += 40+randint(py.misc.lev*2);
              py.flags.resist_heat += 40+randint(py.misc.lev*2);
              break;
            case 24:
             if (get_dir(CNIL, &dir))
              fire_ball(GF_MAGIC_MISSILE, dir, char_row, char_col,
              damroll(6,7),"Blast Wave");
              break;
	    case 25:
              (void) hp_player(8,10);
              (void) cure_poison();
              break;
	    case 26:
              if (get_dir(CNIL, &dir))
	       {
                i=randint(4)+1;
                switch(i)
		  {
		  case 1:
                    fire_ball(GF_LIGHTNING, dir, char_row, char_col,
                    damroll(8,9),"Lightning Ball");
                   break;
                  case 2:
                    fire_ball(GF_FROST, dir, char_row, char_col,
                    damroll(8,9),"Ice Ball");
                   break;
                  case 3:
                    fire_ball(GF_FIRE, dir, char_row, char_col,
                    damroll(8,9),"Fire Ball");
                   break;
                  case 4:
                    fire_ball(GF_MAGIC_MISSILE, dir, char_row, char_col,
                    damroll(8,9),"Wind Ball");
                   break;
		  }
	      }
              break;
            case 27:
              (void) protect_evil();
              break;
	    case 28:
              (void) dispel_creature(CD_EVIL|CD_ANIMAL,py.misc.lev*6);
              break;
            case 29:
              for (dir=0;dir<9;dir++)
               if (dir != 4)
                fire_ball(GF_MAGIC_MISSILE, char_row, char_col,
                 30, "Blue Mist");
              break;
	     default:
             break;
	     }
           if (!free_turn_flag)
	     {
              p_ptr = &py.misc;
              if ((spell_worked & (1L << choice)) == 0)
		{
                 p_ptr->exp += m_ptr->sexp << 2;
                 spell_worked |= (1L << choice);
                 prt_experience();
	       }
	    }
	 }
         p_ptr = &py.misc;
         if (!free_turn_flag)
	   {
            if (m_ptr->smana > p_ptr->cmana)
	      {
               msg_print("You faint from the effort!");
               py.flags.paralysis = randint(60)+5;
               p_ptr->cmana=0;
               p_ptr->cmana_frac=0;
               if (randint(3) == 1)
		 {
                  msg_print("You have parched your throat!");
                  (void) dec_stat (A_CON);
                }
	     }
             else
              p_ptr->cmana -= m_ptr->smana;
             prt_cmana();
	  }
      }
   }
}
