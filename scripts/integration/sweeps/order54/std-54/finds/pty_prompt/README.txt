Not a find: the interactive prompt on a real pty, both backends identical:
  python3 drive.py node prompt.mjs
  python3 drive.py <native prompt binary>
before input: b'name? '
after line 1: b'annx\x08 \x08\r\nhello, ann\r\nagain? '   (typo, Backspace via the line discipline, Enter)
after ctrl-d: b'no answer\r\n'
exit code: 3
