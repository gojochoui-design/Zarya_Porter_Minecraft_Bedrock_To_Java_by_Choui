import os
import sys

P4A = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
    os.getcwd(), ".buildozer", "android", "platform", "python-for-android")


def patch_python3():
    p = os.path.join(P4A, "pythonforandroid", "recipes", "python3", "__init__.py")
    s = open(p).read()
    marker = "ac_cv_header_grp_h=no"
    if marker in s:
        print("python3 recipe already patched")
        return
    old = ("        if _p_version.minor >= 14:\n"
           "            self.patches.append('patches/3.14_armv7l_fix.patch')\n"
           "            self.patches.append('patches/3.14_fix_remote_debug.patch')\n")
    new = ("        if _p_version.minor >= 14:\n"
           "            self.patches.append('patches/3.14_armv7l_fix.patch')\n"
           "            self.patches.append('patches/3.14_fix_remote_debug.patch')\n"
           "        else:\n"
           "            self.configure_args.extend([\n"
           "                'ac_cv_header_grp_h=no',\n"
           "                'ac_cv_func_getgrouplist=no',\n"
           "                'ac_cv_func_getgrent=no',\n"
           "                'ac_cv_func_setgrent=no',\n"
           "                'ac_cv_func_endgrent=no',\n"
           "            ])\n")
    assert old in s, "python3 recipe anchor not found"
    open(p, "w").write(s.replace(old, new, 1))
    print("python3 recipe patched")


def patch_kivy():
    p = os.path.join(P4A, "pythonforandroid", "recipes", "kivy", "__init__.py")
    s = open(p).read()
    old = 'hostpython_prerequisites = ["cython>=0.29.1,<=3.0.12"]'
    new = 'hostpython_prerequisites = ["cython>=3.0.12,<=3.1.6"]'
    if new in s:
        print("kivy recipe already patched")
        return
    assert old in s, "kivy recipe anchor not found"
    open(p, "w").write(s.replace(old, new, 1))
    print("kivy recipe patched")


def patch_archs():
    p = os.path.join(P4A, "pythonforandroid", "archs.py")
    s = open(p).read()
    anchor = "        if 'HOME' in environ:\n            env['HOME'] = environ['HOME']\n"
    extra = ("        for _k in ('PATH', 'ACLOCAL_PATH'):\n"
             "            if _k in environ and _k not in env:\n"
             "                env[_k] = environ[_k]\n")
    if extra in s:
        print("archs.py already patched")
        return
    assert anchor in s, "archs.py anchor not found"
    open(p, "w").write(s.replace(anchor, anchor + extra, 1))
    print("archs.py patched")


if __name__ == "__main__":
    patch_python3()
    patch_kivy()
    patch_archs()
