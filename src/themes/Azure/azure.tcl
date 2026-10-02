# Copyright © 2021 rdbende <rdbende@gmail.com>

source [file join [file dirname [info script]] theme light.tcl]
source [file join [file dirname [info script]] theme dark.tcl]

option add *tearOff 0

proc set_theme {mode} {
	if {$mode == "dark"} {
		ttk::style theme use "azure-dark"

		array set colors {
            -fg             "#ffffff"
            -bg             "#35324a"
            -disabledfg     "#ffffff"
            -disabledbg     "#9585b8"
            -selectfg       "#ffffff"
            -selectbg       "#a99cc8"
        }
        
        ttk::style configure . \
            -background $colors(-bg) \
            -foreground $colors(-fg) \
            -troughcolor $colors(-bg) \
            -focuscolor "#d9a3b8" \
            -selectbackground $colors(-selectbg) \
            -selectforeground $colors(-selectfg) \
            -insertcolor "#d9a3b8" \
            -insertwidth 1 \
            -fieldbackground $colors(-selectbg) \
            -font {"Segoe Ui" 10} \
            -borderwidth 1 \
            -relief flat

        tk_setPalette background [ttk::style lookup . -background] \
            foreground [ttk::style lookup . -foreground] \
            highlightColor [ttk::style lookup . -focuscolor] \
            selectBackground [ttk::style lookup . -selectbackground] \
            selectForeground [ttk::style lookup . -selectforeground] \
            activeBackground [ttk::style lookup . -selectbackground] \
            activeForeground [ttk::style lookup . -selectforeground]

        ttk::style map . -foreground [list disabled $colors(-disabledfg)]

        option add *font [ttk::style lookup . -font]
        option add *Listbox.background "#35324a"
        option add *Text.background "#35324a"
        option add *Menu.selectcolor $colors(-fg)
    
	} elseif {$mode == "light"} {
		ttk::style theme use "azure-light"

        array set colors {
            -fg             "#000000"
            -bg             "#efeaf7"
            -disabledfg     "#737373"
            -disabledbg     "#efeaf7"
            -selectfg       "#ffffff"
            -selectbg       "#8b7bbd"
        }

		ttk::style configure . \
            -background $colors(-bg) \
            -foreground $colors(-fg) \
            -troughcolor $colors(-bg) \
            -focuscolor "#e08fb0" \
            -selectbackground $colors(-selectbg) \
            -selectforeground $colors(-selectfg) \
            -insertcolor $colors(-fg) \
            -insertwidth 1 \
            -fieldbackground $colors(-selectbg) \
            -font {"Segoe Ui" 10} \
            -borderwidth 1 \
            -relief flat

        tk_setPalette background [ttk::style lookup . -background] \
            foreground [ttk::style lookup . -foreground] \
            highlightColor [ttk::style lookup . -focuscolor] \
            selectBackground [ttk::style lookup . -selectbackground] \
            selectForeground [ttk::style lookup . -selectforeground] \
            activeBackground [ttk::style lookup . -selectbackground] \
            activeForeground [ttk::style lookup . -selectforeground]

        ttk::style map . -foreground [list disabled $colors(-disabledfg)]

        option add *font [ttk::style lookup . -font]
        option add *Listbox.background "#f8f6fc"
        option add *Text.background "#f8f6fc"
        option add *Menu.selectcolor $colors(-fg)
	}
}
