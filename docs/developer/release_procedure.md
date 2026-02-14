# Release procedure

1. write release notes
1. update Python
    - make sure `PATH` points to the latest Python release
    - run `python -m venv --upgrade .venv`
1. update pip packages
    - run `packaging/scripts/upgrade_all_pip_packages.py`
1. run tests
1. freeze pip dependencies
    - run `pip freeze >requirements.txt`
1. increment version number
    - in `src/utilities/constants`
    - in `packaging/windows/installer_setup.iss`
1. create Windows installer
    1. run `pyinstaller packaging/windows/kapytal.spec`
    1. compile `packaging/windows/installer_setup.iss` with InnoSetup
    1. test the installer
    - do NOT run Kapytal from `dist/` directory!
1. create Linux AppImage
    1. run `pyinstaller packaging/linux/kapytal.spec`
    1. copy contents of `dist/Kapytal` to `packaging/linux/Kapytal.MainDir/`
    1. run `appimagetool Kapytal.MainDir`
    1. test the AppImage
    - do NOT run Kapytal from `dist/` folder!
1. prepare release on Git
    1. merge Git branch `develop` into `master`
        1. `git checkout master`
        1. `git merge develop --no-ff`
    1. create Git tag with message
        - `git tag -a vX.X`
        - text editor will open, paste in handwritten release notes
    1. push Git tag
        - `git push origin vX.X`
1. create release on GitHub
    1. create release from tag vX.X
    1. add generated release notes
    1. add handwritten release notes
    1. attach Windows installer
    1. attach Linux AppImage
