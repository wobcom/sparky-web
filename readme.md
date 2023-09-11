# SPARKY Web

A webinterface for managing SPARKY probes and the Headscale server.

## Dev-Environment
If you use [Nix](https://nixos.org/), you can get a environment with all required python packages by running
```console
nix develop
```
If you want to use PyCharm for development, you can run
```console
nix build .#python-env
```
and then add `result/bin/python3` as a system interpreter to PyCharm.