let
  pypiDataRev="7f28322aa7baec80e261002076e7b322f153e12f";
  pypiDataSha256="1dj7dg4j0qn9a47aw9fqq4wy9as9f86xbms90mpyyqs0i8g1awjz"; ## commit: master # 2021-08-29T07:53:42Z # DavHau/pypi-deps-db
  mach-nix = import (builtins.fetchGit {
    url = "https://github.com/DavHau/mach-nix/";
    ref = "3.3.0";
  }) {
    inherit pypiDataRev pypiDataSha256;
  };
  pkgs =  mach-nix.nixpkgs;
  cottonmouth = mach-nix.buildPythonPackage {
    name = "cottonmouth";
    src = builtins.fetchGit {
      url = "https://github.com/adamlwgriffiths/cottonmouth";
      ref = "master";
      rev = "34b20827200b41208b2e5a90b4d9c713a74e4939";
    };
  };
  custom-python = mach-nix.mkPython {
    python = "python38";
    requirements = ''
      PyGObject>=3.40.1
      pywebview>=3.5
      flask>=2.0.1
      flask-socketio>=5.1.1
      python-socketio>=5.4.0
      eventlet>=0.31.1
      brython>=3.9.5
    '';
    packagesExtra = [
      cottonmouth
    ];
    providers = {};
  };
in pkgs.mkShell {
  nativeBuildInputs = with pkgs; [
    gobject-introspection
  ];

  buildInputs = with pkgs; [
    custom-python
    gtk3
    webkitgtk
  ];
}
