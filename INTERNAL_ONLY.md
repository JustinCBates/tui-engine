This repository is internal-only and has not been published or released externally.

Policy:
- Backwards-incompatible changes may be made without shims or deprecation periods.
- The project does not maintain compatibility guarantees with external consumers.

If you are a contributor: prefer explicit imports for internal subpackages, e.g.:

    import tui_engine.factories as widgets

instead of relying on package re-exports in `tui_engine.__init__`.

This file is intentionally short; it documents the current policy and can be extended
if/when the project moves toward a public release.
