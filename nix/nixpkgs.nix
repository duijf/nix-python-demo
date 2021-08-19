# This file imports Nixpkgs at a specific commit. It is written in the Nix language.
#
# Nixpkgs is:
#
#  - A collection of software (both language specific libraries and system tools).
#  - A standard library of utilities to accomplish useful tasks in Nix. Examples are:
#    `pkgs.mkShell` for local dev environments and `pkgs.dockerTools.buildImage` to
#    create minimal Docker images.
#
# Nixpkgs is a huge collection of software. You can search for what packages it has
# at [1]. It's developed on GitHub and the repository can be found at [2].
#
# [1] https://search.nixos.org/packages
# [2] https://github.com/nixos/nixpkgs
#
# In the Nix language, files are a single expression. There is support for
# constant variables, functions, strings, numbers. Nix is a pure functional
# programming language, but is not statically typed. It's kind of weird, but
# if you get used to it, you can make pretty sweeping changes to your tools.
#
# Examples of what you can do with Nix and Nixpkgs:
#
#  - Exactly reproduce a build result, such as a package, user environment,
#    Docker image, Linux distro, Linux image, AWS AMI, Google Cloud image, etc.
#  - Make sweeping changes to dependencies. Builds are specified from source,
#    but there are binary caches available. Want to run Postgres with a custom
#    set of patches? It's easy to do so across prod machines and dev environments
#    at the same time.
#  - Have two versions of the same package installed side by side. Easily switch
#    between them if they are in cache. Easily switch between branches without
#    rebuilding some Docker images.

let
  # Fetch a .tar.gz archive from the internet. We include the sha256 hash which is
  # checked by Nix for reproducibility. In Nix lingo, this is sometimes referred to
  # as a "fixed output derivation".
  pkgsTarball = fetchTarball {
    url = "https://github.com/NixOS/nixpkgs/archive/0747387223edf1aa5beaedf48983471315d95e16.tar.gz";
    sha256 = "sha256:19hpz87vfcr6icxcjdlp2mnk8v5db4l3x32adzc5ynmxvfayg3lr";
  };
in
  # `pkgsTarball` resolves to a directory on disk in which the extracted
  # contents of the tarball are placed. This directory is placed in the "Nix
  # store", a special directory that is managed by Nix and placed at
  # `/nix/store`.
  #
  # If you give the `import` statement a path, it will look for a file
  # `default.nix` at that path and load it's contents. The `default.nix`
  # file can be found on disk or on GitHub [3].
  #
  # This file is yet more Nix code, which evaluates the entire set of
  # packages and returns it as an "attribute set". Better names for
  # "attribute set" would be "map", "dictionary" or "associative array".
  #
  # [3]: https://github.com/NixOS/nixpkgs/blob/master/default.nix
  import pkgsTarball
