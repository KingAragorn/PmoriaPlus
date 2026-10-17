cmake_minimum_required(VERSION 3.10)
project(PmoriaPlus C)

include(GNUInstallDirs)

set(CURSES_NEED_NCURSES TRUE)
find_package(Curses REQUIRED)

set(PMORIA_SOURCES
  source/main.c
  source/misc1.c
  source/misc2.c
  source/misc3.c
  source/misc4.c
  source/store1.c
  source/files.c
  source/io.c
  source/create.c
  source/desc.c
  source/generate.c
  source/sets.c
  source/dungeon.c
  source/creature.c
  source/death.c
  source/eat.c
  source/help.c
  source/magic.c
  source/potions.c
  source/prayer.c
  source/save.c
  source/staffs.c
  source/wands.c
  source/scrolls.c
  source/spells.c
  source/wizard.c
  source/store2.c
  source/signals.c
  source/moria1.c
  source/moria2.c
  source/moria3.c
  source/moria4.c
  source/monsters.c
  source/treasure.c
  source/variable.c
  source/rnd.c
  source/recall.c
  source/unix.c
  source/player.c
  source/tables.c
  source/incant.c
)

add_executable(pmoria ${PMORIA_SOURCES})
target_include_directories(pmoria PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/source
  ${CURSES_INCLUDE_DIRS}
)
target_compile_definitions(pmoria PRIVATE
  unix
  "MORIA_LIB_SOURCE=\"${CMAKE_SOURCE_DIR}/files\""
  "MORIA_LIB_DEFAULT=\"${CMAKE_INSTALL_FULL_DATADIR}/pmoria\""
)
target_link_libraries(pmoria PRIVATE ${CURSES_LIBRARIES})

if(CMAKE_C_COMPILER_ID MATCHES "GNU|Clang|AppleClang")
  target_compile_options(pmoria PRIVATE
    -std=gnu17
    -fcommon
    -Wall
    -Wno-unknown-warning-option
    -Wno-unused-parameter
    -Wno-unused-variable
    -Wno-unused-function
    -Wno-unused-but-set-variable
    -Wno-pointer-sign
    -Wno-format
    -Wno-unused-result
    -Wno-deprecated-declarations
    -Wno-old-style-definition
    -Wno-missing-braces
    -Wno-implicit-fallthrough
    -Wno-sign-compare
    -Wno-parentheses
    -Wno-char-subscripts
    -Wno-int-to-pointer-cast
    -Wno-pointer-to-int-cast
    -Wno-missing-field-initializers
  )
endif()

install(TARGETS pmoria RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR})
install(FILES
  files/hours
  files/news
  files/origcmds.hlp
  files/owizcmds.hlp
  files/roglcmds.hlp
  files/rwizcmds.hlp
  files/version.hlp
  files/welcome.hlp
  DESTINATION ${CMAKE_INSTALL_DATADIR}/pmoria
)
