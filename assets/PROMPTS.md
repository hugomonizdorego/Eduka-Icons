# Clay master prompts (0.3.0)

Method: built-in image generation, one call per asset, with the user's image as
the style reference and a transparent alpha background. The 17 results are the
lossless masters in `assets/masters/`.

Base prompt: ONE isolated Linux desktop icon for Eduka-Icons 0.3.0.
The uploaded image is the definitive style reference. Match its handmade
sculpted clay material, thick soft rounded edges, tiny matte grain,
cream/ivory, burnt orange, golden yellow, muted olive and pale dusty aqua,
gentle top-left lighting and neutral contact shadow. Freestanding physical
object, nearly front view with slight right-side depth, filling 82–84% of a
square canvas with even transparent padding. True transparent alpha.
No app tile, no opaque backdrop, no scene, no glow, no gloss, no text.

| Asset | Subject |
| --- | --- |
| folder | Open aqua folder, cream tab, ivory sheets, cream clasp with an orange button. |
| home | Ivory house, thick yellow roof, orange chimney, olive door, aqua window. |
| browser | Ivory compass, charcoal ring, orange/yellow needle; aqua/olive/gold map behind it. |
| camera | Ivory/olive instant camera, charcoal lens, yellow button, orange print, mountain photo behind. |
| education | Olive backpack, ivory flap, orange pouch, yellow buckle and clay stitching. |
| files | Olive suitcase, ivory top and handle, orange/yellow latches. |
| settings | Ivory gear with eight rounded teeth, yellow centre, orange axle, olive sides. |
| terminal | Charcoal monitor, ivory bezel, olive stand, orange chevron, ivory underscore. |
| document | Ivory paper with folded corner, olive lines, yellow tab, orange pencil. |
| music | Olive radio, ivory face, charcoal speaker, orange dial, yellow handle. |
| mail | Ivory envelope, triangular flap, orange wax seal, olive side, slightly tilted. |
| chat | Two ivory/olive speech bubbles, three orange dots, sculpted tails. |
| store | Ivory shopping bag, olive side, yellow handle, orange clay parcel in front. |
| shield | Olive shield, ivory rim, yellow check, orange padlock at the lower right. |
| bulb | Yellow bulb, orange filament, ivory/olive screw base, no glow. |
| calendar | Ivory calendar, orange bar, yellow rings, olive grid, one orange date, no numbers. |
| trash | Ivory wastebasket, olive ribs, yellow lid, orange knob. |

All other artwork is composed in code (`tools/artwork.py`, `tools/clay.py`)
and rendered offline by `tools/prepare_clay.py`.
