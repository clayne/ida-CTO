# CTO (Call Tree Overviewer)

CTO (Call Tree Overviewer) is an IDA plugin for creating a simple and efficiant function call tree graph. It can also summarize function information such as internal function calls, API calls, static linked library function calls, unresolved indirect function calls, string references, structure member accesses, specific comments.

CTO has another helper plugin named "CTO Function Lister", although it can work as a standalone tool. You can think this is an enhanced version of functions window. It lists functions with summarized important information, which is the same as the CTO's one. You can use a regex filter to find nodes with a specific pattern as well.

![CTO-logo](/logo/CTO-Logo-Body.png)
[![Introducing CTO](https://img.youtube.com/vi/zVCpb82UfFs/maxresdefault.jpg)](https://youtu.be/zVCpb82UfFs)

An introduction video is here.  
https://youtu.be/zVCpb82UfFs

Check the article below about how to use CTO and CTO Function Lister in malware analysis tasks.
https://www.iij.ad.jp/en/dev/iir/pdf/iir_vol59_focus1_EN.pdf

You can also check the presentation at VB2021 localhost.  
https://vblocalhost.com/conference/presentations/cto-call-tree-overviewer-yet-another-function-call-tree-viewer/

Submitted paper  
https://vblocalhost.com/uploads/VB2021-Suzuki.pdf

Presentation slides  
https://vblocalhost.com/uploads/2021/09/VB2021-14.pdf

## Requirements
- IDA Pro 7.4 or later (I tested on 7.4 SP1, 8.0, 8.2 SP1, 8.4 SP2, 9.0, and 9.0 SP1)
- Python 3.x (I tested on Python 3.8 to 3.12)

You will need at least IDA Pro 7.4 or later because of the APIs that I use.

## Optional 3rd Party Software
- ironstrings  
  https://github.com/fireeye/flare-ida/tree/master/python/flare/ironstrings

- findcrypt.py  
  https://github.com/you0708/ida/tree/master/idapython_tools/findcrypt

- findguid.py  
  https://github.com/you0708/ida/tree/master/idapython_tools/findguid

- SusanRTTI  
  https://github.com/nccgroup/SusanRTTI

- IDA_Signsrch  
  https://sourceforge.net/projects/idasignsrch/

- yara4ida  
  https://github.com/kweatherman/yara4ida

- Class Informer  
  https://sourceforge.net/projects/classinformer/  
  https://github.com/herosi/classinformer

## How to Install
See "[INSTALL](/INSTALL)" file.

## How to Use
To start CTO, press Alt+Shift+C.

Double-click "..." symbol if you want to expand the path.
If you want to create a graph based on a different target function, jump to the target function, click the CTO window, and press "F" key.
See the help by pressing "H" key on the CTO window.

To start CTO Function Lister, press Alt+Shift+F. See the help by pressing "H" key on the CTO Function Lister window as well.

Check the articles showed in the top of this file as well.

## Note
CTO is still under development and it is unstable yet. I might change the data structure drastically.
CTO accesses sensitive internal data structure of IDA such as low level APIs and PyQt5. And it might cause a crash of IDA.
Do not use this in important situations. I don't take responsibility for any damage or any loss caused by the use of this.

I'm not a programmer. I'm a malware analyst. Please do not expect product-level code.

PRs are welcome. Just complaining and a bug report without enough information are NOT welcome ;-)

## Known Issues
- Currently, CTO focuses on Intel x64/x86 architecture. If you want to extend other architectures, please send the PR to me.

