echo off
echo mostro les branques local (asterisc en la activa)
git branch
echo .
echo mostro el directori del repositori actual
git rev-parse --show-toplevel
echo .
echo actualitzo la informcio sobre el repositoris remot
git fetch origin
echo .
echo mostro els repositoris remots configurats
git remote -v
echo .
echo mostro les branques del repositori remot
git branch -r
