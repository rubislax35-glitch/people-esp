[app]
title = People ESP
package.name = peopleesp
package.domain = org.codex.peopleesp
source.dir = .
source.include_exts = py,kv,png,jpg,atlas
version = 0.1
requirements = python3,kivy,numpy,opencv
orientation = portrait
fullscreen = 0
android.permissions = CAMERA
android.api = 35
android.minapi = 23
android.archs = arm64-v8a
android.accept_sdk_license = True
p4a.branch = develop

[buildozer]
log_level = 2
warn_on_root = 1

