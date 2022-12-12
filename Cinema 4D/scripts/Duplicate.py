from typing import Optional
import c4d

doc: c4d.documents.BaseDocument  # The active document
op: Optional[c4d.BaseObject]  # The active object, None if unselected

def main() -> None:
 c4d.CallCommand(12107) # Copy
 c4d.CallCommand(12108) # Paste

if __name__ == '__main__':
    main()