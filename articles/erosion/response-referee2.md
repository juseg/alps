<!-- Copyright (c) 2021, Julien Seguinot (juseg.github.io), Ian Delaney
Creative Commons Attribution-ShareAlike 4.0 International License
(CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/) -->

# Authors' response to Ian Evans

Dear Ian Evans,

Thank you very much for your detailed review of our manuscript.

## General Comments

> The authors provide large amounts of very useful results from simulations,
> concerning the effects of varying glacier geometry on erosion potential. It
> was quite an achievement to compute this at fairly high temporal and spatial
> resolution (1 km and 50 a throughout the Alps). The conclusions are
> reasonable, and I value the results. They provide support for the
> traditional view, that high-altitude features such as cirques are eroded by
> steep, local glaciers and not under extensive icefields well above ELA. Most
> erosion is expected along major valleys (glacial troughs): the potential
> erosion is greatest low down the glaciers, with a lesser maximum at high
> altitude and a minimum between. The paper is well written and the Figures
> are all relevant and interesting. The qualitative conclusions are well
> justified.

> An interesting result, not commented on, is that from Figs. 3 and 7 i & j,
> potential erosion volume in the Alps peaks when ice cover amounts to 1.6 cm
> sea level equivalent. I would love to see a map of the glaciers at that
> stage\*, which is well below maximum but considerably more than recent ice
> cover (0.3 ± 0.1 mm s.l.e., Farinotti et al. 2019). This peak applies to the
> ‘Koppes’ and ‘Herman’ erosion laws, but not to ‘Humphrey’ and ‘Cook’ laws
> which give very broad maxima for s.l.e. 10-30 cm (Fig. 7 k & l).

Thank you for pointing this out. We are not confident that this result is
significant. The situation you describe occurs, for instance, during much of
MIS~5 (Fig. 2) and can be visualized in the animations. During such periods,
glaciers are steep and only a few grid cells in width. Their velocities and
thus computed erosion rates may be overestimated by the limiting horizontal
resolution and the shallow-ice physics (Imhof et al., 2019).

Increasing ice volume yields the build-up of less steep and thus slower-flowing
valley glaciers. Decreasing ice volume yields to (roughly) equally steep but
smaller glaciers. In the case of non-linear erosion laws ('Koppes' and 'Herman'
laws), both yield a decrease of erosion volume, hence the local peak in erosion
volume. We now emphasize this uncertainty in several of our plots by using
hatches over areas of limited glacier cover, documented in the figure captions.

> As the comment (lines 221-222) on erosion distribution during advance,
> retreat and maxima is of great interest, it would be useful to illustrate
> this with three maps of potential erosion during each of these types of
> phase.

Figure 4 was reworked to include a map of Rhine glacier modelled erosion rates
at 36 ka, corresponding to the last marjor advance phase before the LGM and with
somewhat similar extent to the deglacial state of 16 ka. This also corresponds
to the topographic profiles shown on Fig. 8.

> I find no mention of lithology, rock type, geology, resistance or erodibility
> (excluding that citing Herman on line 56). This omission of half the erosion
> equation should be mentioned; it implies that the ‘potential’ nature of the
> erosion should be emphasised repeatedly. This adds to the admitted
> limitations of lack of feedback to changing topography, absence of hydrology
> and absence of subglacial sediment accumulation or movement. Using constant
> topography might be OK for the last glaciation, as here, but would become
> increasingly unrealistic for several glaciations. Destinations of eroded
> material are not considered: deposition in temporary storage may inhibit
> erosion in parts. The omission of hydrological processes must be a major
> drawback, as Herman et al. (2011), Egholm et al. (2012a, b) and Pedersen et
> al. (2014) showed that its inclusion of subglacial meltwater, plus horizontal
> stress gradients, gave more realistic simulations of erosion. For erosion
> rate as well as for cumulative erosion, it is potential erosion that is
> calculated, rather than predicted erosion.

TODO: discuss lithology, go through entire text?

> A further necessary geographical qualification concerns the misfit between
> simulated and actual glacier extent. The latter is well established from
> mapping of moraines. It is necessary to check Seguinot et al. (2018) to see
> that all the models predict too much ice in the southwest (south of 45° N)
> and far too much in the east (Sava, Drava, Mur, Enns and Traun valleys),
> while the EPICA models produce too little in the west (Rhône and Jura). I
> agree that this is probably because while the amount of precipitation is
> changed, the spatial pattern is not: thus the orographic effect of ice
> build-up increasing precipitation shadow, and the circulation changes due to
> southward shift of westerlies at LGM, are not included. To make this paper
> more self-contained, a brief mention of the 2018 evaluation is in order.
> Once a more realistic LGM precipitation pattern is accepted, future modelling
> might use gradations between that and the present pattern as a function of
> temperature.


The LGM outline was added on Fig. 2.

TODO: discuss shortly the discrepancy in "climate sensitivity".

> Overall, the paper reports on a very worthwhile computer-intensive exercise.
> It is densely packed with results and repays a careful read and a study of
> the videos. Clearly there can be interesting comparisons with Lai and Anders
> (2021) very recent submission to esurf !

TODO: check that out.

>   [\*That stage can be approximated by pausing the first erosion
>    rates video around 99 ka and 13 ka. The three videos are strongly
>    recommended!]

> The text is short and pithy, so there is space for some extension. There are
> a few missed opportunities, and some incompleteness in the presentation. In
> detail I suggest the following improvements:

## Specific comments - Text:

> The 1 km resolution of the modelling is clearly important, so it is strange
> that the first mention is on p.11. Although it is very demanding of computer
> time, it is still (as admitted) not adequate to represent cirques (averaging
> of the order of 700 m across). Even stranger, there is no mention of the DEM
> used (it was SRTM in the 2018 paper). This information should be provided in
> section 2, p. 3-4.

TODO: The input SRTM topography was mentioned in [...] and in the caption of
Fig. 2.

> The lateral constraints on valley glaciers are usually covered by a ‘form
> factor’: how are they handled by this version of the PISM ice sheet model –
> how has lateral drag been included?

> It might be pointed out that the ‘Koppes’ relationship with an exponent of
> 2.34 is based on 13 data points that are very poorly distributed: in fact,
> Koppes et al. (2015) go on to drop two outliers and reach an exponent of
> 2.62.

> In lines 206-209, the point about trimlines, relating them to
> time-transgressive erosion, is well taken. But they represent the integrated
> effect of many phases of glacial erosion (as noted on 223-224), not
> necessarily just from recessional phases.

## - Figures:

> In Fig. 3 is almost impossible to follow the brown lines, unless advancing
> and retreating parts of lines are distinguished (e.g. by colour). (The ice
> volume video may help out.)  Also: keep to ‘potential erosion volume’. The
> pale brown bars show a decline in annual erosion volume with ice volumes over
> 1.8 cm s.l.e., stronger than is implied in line 110 of the text – it is more
> than ‘slight’.

We applied different colours for periods of increasing and decreasing ice
volume. This actually strikingly highlights the two different regimes. Thank
you for the suggestion. The label was changed to 'potential annual erosion
volume'.

TODO: not so slight decrease.

> To aid interpretation of Figs 4 a-c and 7 a-d, a corresponding topographic
> map or hillshade of the Rhine area on the same scale should be provided.

In addition to the aforementioned changes to Fig. 4, a new panel was added for
the model final state at 0 ka, revealing the bedrock topography.

> Fig. 1c illustrates a very unusual cirque, with a huge lake replacing a very
> unhealthy convex glacier. Fascinating, but surely a more representative
> cirque should be used. Actually these three photos are not well integrated
> with the text (pace lines 191 & 195-198). Lauterbrunnen is an extreme
> (vertical-sided) trough example, over-used by textbooks.

> Fig. 5: The elevation histogram in Fig. 5a could be misleading, as it seems
> to cover the whole study area, including parts never glacier-covered. It
> should be limited to areas glacier-covered at the maximum, and preferably
> supplemented by a histogram for those covered now or at the minimum. The
> accompanying main graph (5a) relates to areas glacier-covered at each time
> slice. Re another reviewer’s comment, yes LGM glaciers did reach below 500 m:
> at L. Garda (67 m?) and the Tagliamento Glacier lobe LGM ice reached below
> 100 m. An integrated plot of total-cycle potential erosion rate (and
> volume?) at each altitude, over glacier-covered areas, would be interesting
> (as an extra Figure): can rates at high altitude, where glacial duration is
> longer, catch up with those at low altitude?  Probably not, given the
> concentration of flow down major valleys. Striping above 3000 m, presumably
> related to low surface area, suggests a switch there to 20 m or 40 m bands
> would be advisable. Caption; ‘modelled potential erosion rates’?

> In Fig. 7, the quantitative contrasts between the ‘Koppes’ law (e) and the
> others are alarming. If the scales are taken literally, (e) gives potential
> erosion around 1 m, while (f) and (g) give hundreds of m, in 120 ka. As 120
> ka is only a fraction of the Quaternary, hundreds of m seems too much, while
> 1 m seems very low (0.008 mm a-1 overall). For me, there should be a correct
> answer between these extremes. The spatial pattern, however, is more
> important.

> Fig. 8a shows a flat dome at 3000 m for about the first 20 km of the Rhine.
> As there are mountains at 3630, 3583 and 3192 m around the sources, it is
> likely that   there would be steeper ice slopes up to these peaks, giving
> rather different stresses and erosion potentials. Also are the instabilities
> in Fig. 8b, near source and terminus, edge effects or related to the 1 km
> resolution?

>   The three videos are well worth watching  -in fact they clarify some
>   queries arising from the paper. Perhaps they could be captioned in the
>   ‘Video supplement’ paragraph. Some extra information on the third (bedrock
>   altitude) video could point out that there are numerous zero values not
>   shown: the zero geometric mean rates from 2300 to 3000 m around 24 ka
>   otherwise seem to conflict with the numerous positive rates plotted. Zero
>   rates presumably show where ice is frozen to the bed: their altitudinal
>   distribution might be worth discussion in the text. Above 3000 m means are
>   positive, which seems strange.

## Technical corrections:

> All map figures need km scale bars.

Scale bars were added on all map figures.

> Line 24  ‘are yet’

> 27 ‘in the absence’

> 38 ‘Examination … suggests’

> 61 ‘modelled erosion potential’ rather than ‘ modelled erosion rates’ ?

> 70 insert ‘isostatic’?

> 72 ‘and is run to…’

> 78 ‘temperature lapse-rate’ or is it ‘temperature change’ ?

> 116-7 ‘much of the’; and delete comma after bracket.

> 161 ‘does not increase’

> 190 delete both commas

## References not in original:

> Egholm, D.L., Pedersen, V.K., Knudsen, M.F., Larsen, N.K., 2012a. Coupling
> the flow of ice, water, and sediment in a glacial landscape evolution model.
> Geomorphology 141–142: 47–66.
> http://dx.doi.org/10.1016/j.geomorph.2011.12.019.

> Egholm, D.L., Pedersen, V.K., Knudsen, M.F., Larsen, N.K., 2012b. On the
> importance of higher-order ice dynamics for glacial landscape evolution.
> Geomorphology 141–142: 67-80.

> Farinotti, D., et al., 2019. A consensus estimate for the ice thickness
> distribution of all glaciers on Earth. Nat. Geosci. 12, 168–173.

> Lai, J., Anders, A.M., 2021. Climatic controls on mountain glacier basal
> thermal regimes dictate spatial patterns of glacial erosion.
> https://esurf.copernicus.org/preprints/esurf-2021-26/

> Pedersen, V.K., Huismans, R.S., Herman, F., Egholm, D.L., 2014. Controls of
> initial topography on temporal and spatial patterns of glacial erosion.
> Geomorphology 223, 96-116.

## Acknowledgements:

> I am grateful for helpful discussions with Iestyn Barr, Jeremy Ely, Matt
> Tomkins, Pippa Whitehouse, Cristina Balaban and Matt Wiecek.

> - Ian S. Evans, Durham University, U.K.
