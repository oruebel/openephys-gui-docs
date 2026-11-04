# NWB format figures

`make_nwb_figures.py` generates the file-organization figures of the NWB format page
(`source/_static/images/recordingdata/nwb/{organization,continuous,events,spikes}.png`) for version 2.0 of
the NWB Format plugin.

The figures follow the style of the other format figures, which are drawn in
`source/_static/images/recordingdata/format-illustrations.ai`:

- The icons in `icons/` are cropped from the previous NWB figures.
- The text uses Source Sans Pro SemiBold.
- The line width, font size, and spacing are measured from the previous figures.

`format-illustrations.ai` still contains the previous NWB figures. If you prefer to keep all figures in
Illustrator, redraw the NWB figures there; the trees are defined in `FIGURES` in the script, and you can
delete this directory.

## Usage

Requires Python 3 and ImageMagick 7 (`magick`). Download Source Sans Pro SemiBold (SIL Open Font License),
e.g., `OTF/SourceSansPro-Semibold.otf` from https://github.com/adobe-fonts/source-sans/releases/tag/2.040R-ro%2F1.090R-it,
then run from the repository root:

```bash
python3 tools/nwb-figures/make_nwb_figures.py SourceSansPro-Semibold.otf
```

This overwrites the figures in `source/_static/images/recordingdata/nwb/`. To change a figure, edit its tree
in `FIGURES`.
