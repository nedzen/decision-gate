Output demo-agent.gif
Set FontSize 22
Set Width 1200
Set Height 675
Set Padding 30
Set TypingSpeed 20ms
Set Theme { "background": "#1e1e2e", "foreground": "#cdd6f4", "cursor": "#f5e0dc", "black": "#45475a", "green": "#a6e3a1", "yellow": "#f9e2af", "red": "#f38ba8", "blue": "#89b4fa", "magenta": "#cba6f7", "cyan": "#94e2d5", "white": "#cdd6f4", "brightBlack": "#585b70", "brightGreen": "#a6e3a1", "brightYellow": "#f9e2af", "brightRed": "#f38ba8", "brightBlue": "#89b4fa", "brightMagenta": "#cba6f7", "brightCyan": "#94e2d5", "brightWhite": "#ffffff" }

Type "# an agent session with selective ingestion — every gate call below is real" Enter
Sleep 700ms
Type "python3 examples/agent_loop.py --results examples/results.tsv --pages examples/pages/ --task 'how do people use decision models to cut agent costs?'" Enter
Sleep 3200ms
Sleep 1500ms

Type@0 "clear" Enter
Sleep 300ms
Type@0 "echo ''" Enter
Type@0 "echo '  selective ingestion: the agent read 6 of 12 results'" Enter
Type@0 "echo '  context: 745 tok instead of 1866 tok  (60% saved)'" Enter
Type@0 "echo '  gate spend: ~\$0.0001 for the whole session'" Enter
Type@0 "echo ''" Enter
Type@0 "echo '  github.com/nedzen/decision-gate  -  Jev API or 100% local via Laya'" Enter
Type@0 "echo ''" Enter
Sleep 2500ms
