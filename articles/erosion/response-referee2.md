<!-- Copyright (c) 2021, Julien Seguinot (juseg.github.io), Ian Delaney
Creative Commons Attribution-ShareAlike 4.0 International License
(CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/) -->

# Authors' response on RC2

Dear Ian Evans,

Thank you very much for your and your colleague's time in preparing this review of our manuscript. We try to address your comments one by one below, and highlight relevant changes made to the manuscript.


## General Comments

> The authors provide large amounts of very useful results from simulations, concerning the effects of varying glacier geometry on erosion potential. It was quite an achievement to compute this at fairly high temporal and spatial resolution (1 km and 50 a throughout the Alps). The conclusions are reasonable, and I value the results. They provide support for the traditional view, that high-altitude features such as cirques are eroded by steep, local glaciers and not under extensive icefields well above ELA. Most erosion is expected along major valleys (glacial troughs): the potential erosion is greatest low down the glaciers, with a lesser maximum at high altitude and a minimum between. The paper is well written and the Figures are all relevant and interesting. The qualitative conclusions are well justified.

> An interesting result, not commented on, is that from Figs. 3 and 7 i & j, potential erosion volume in the Alps peaks when ice cover amounts to 1.6 cm sea level equivalent. I would love to see a map of the glaciers at that stage\*, which is well below maximum but considerably more than recent ice cover (0.3 ± 0.1 mm s.l.e., Farinotti et al. 2019). This peak applies to the ‘Koppes’ and ‘Herman’ erosion laws, but not to ‘Humphrey’ and ‘Cook’ laws which give very broad maxima for s.l.e. 10-30 cm (Fig. 7 k & l).
>
>   [\*That stage can be approximated by pausing the first erosion rates video around 99 ka and 13 ka. The three videos are strongly recommended!]

Thank you for pointing this out. However, we are not confident that this result is significant. The situation you describe occurs, for instance, during much of MIS~5 (Fig. 2) and can be visualized in the animations (as you noted). During such periods, glaciers are steep and only a few grid cells in width.

Increasing ice volume yields the build-up of less steep and thus slower-flowing valley glaciers. Decreasing ice volume leads to (roughly) equally steep but smaller glaciers. In the case of non-linear erosion laws ('Koppes' and 'Herman' laws), both yield a decrease of erosion volume, hence the local peak in erosion volume. However, we would rather not highlight this result. The modelled glacier velocities for such situations are unreliable due to the limiting horizontal resolution and the shallow-ice physics. This latter fact was highlighted in a new passage in the section on the "age of the glacial landscape". Also including suggestions from reviewer #1, the new passage reads as follow:

    "The validity of the model results at high elevation is discussable.  Cristalline massifs such as the Ecrins, Gran Paradiso, Monte Rosa, Aare, Ötztal and Tauern Massifs locally exhibit a strikingly high erosion potential. However, the computation of glacier flow velocities on such steep surfaces is strongly limited by the model horizontal resolution of 1\,km, the shallow-ice glacier flow physics (Imhof et al., 2019), and PISM's current mass-conservation heuristics (Imhof, 2021). Besides, bergschrund (rimaye) processes likely to dominate interglacial cirque erosion at such altitudes (Sanders et al., 2012) are not captured by the velocity-based glacier erosion power-laws."

To avoid over-interpretation from future readers, this uncertainty was also highlighted in several of our plots (including Figs. 3 and 7) using hatches over periods of limited glacier volume, and documented in the figure captions.

> As the comment (lines 221-222) on erosion distribution during advance, retreat and maxima is of great interest, it would be useful to illustrate this with three maps of potential erosion during each of these types of phase.

Thank you. Figure 4 was reworked to include a map of Rhine glacier modelled erosion rates at 36 ka, corresponding to the last major advance phase before the LGM and with a similar extent to the deglacial stage of 16 ka. This also corresponds to the topographic profiles shown on Fig. 8. Thus it seems more appropriate in hindsight.

> I find no mention of lithology, rock type, geology, resistance or erodibility (excluding that citing Herman on line 56). This omission of half the erosion equation should be mentioned; it implies that the ‘potential’ nature of the erosion should be emphasised repeatedly. This adds to the admitted limitations of lack of feedback to changing topography, absence of hydrology and absence of subglacial sediment accumulation or movement. Using constant topography might be OK for the last glaciation, as here, but would become increasingly unrealistic for several glaciations. Destinations of eroded material are not considered: deposition in temporary storage may inhibit erosion in parts. The omission of hydrological processes must be a major drawback, as Herman et al. (2011), Egholm et al. (2012a, b) and Pedersen et al. (2014) showed that its inclusion of subglacial meltwater, plus horizontal stress gradients, gave more realistic simulations of erosion. For erosion rate as well as for cumulative erosion, it is potential erosion that is calculated, rather than predicted erosion.

The above limitations were made explicit with the following added sentences in the methods subsection on the "erosion law":

    "Instead, we assume that eroded material is instantly transported out of the system, thus neglecting its role in shielding the bedrock from glacier erosion in zones of temporary storage (Preusser et al., 2010). Neither do we account for differences in erosion effectiveness on different lithologies or erosion from subglacial and interglacial hydrologic processes. For the aforementioned reasons, we refer to the above computed rates, ė, as “potential erosion rates”."

Second and as implied, the entire text and the figure labels were reworked to replace “erosion rates” with “potential erosion rates” nearly everywhere. To avoid clutter a few sentences still mention “modelled erosion rates” instead of “potential erosion rates”.

> A further necessary geographical qualification concerns the misfit between simulated and actual glacier extent. The latter is well established from mapping of moraines. It is necessary to check Seguinot et al. (2018) to see that all the models predict too much ice in the southwest (south of 45° N) and far too much in the east (Sava, Drava, Mur, Enns and Traun valleys), while the EPICA models produce too little in the west (Rhône and Jura). I agree that this is probably because while the amount of precipitation is changed, the spatial pattern is not: thus the orographic effect of ice build-up increasing precipitation shadow, and the circulation changes due to southward shift of westerlies at LGM, are not included. To make this paper more self-contained, a brief mention of the 2018 evaluation is in order.  Once a more realistic LGM precipitation pattern is accepted, future modelling might use gradations between that and the present pattern as a function of temperature.

The field-based LGM outline was added on Fig. 2 (Alps-wide map of cumulative erosion potential). In addition, the following sentences were added in the "climate sensitivity" section of the discussion mentioning the general eastwards bias of our results with regard to field evidence:

    "It should be noted, however, that all runs presented here show a systematic bias with excessive glacier cover in the Eastern Alps and a diminished glacier extent in the Western Alps (Fig. 2a; further discussed in Seguinot et al., 2018). Thus the modelled patterns of erosion potential certainly includes a similar bias."

> Overall, the paper reports on a very worthwhile computer-intensive exercise.  It is densely packed with results and repays a careful read and a study of the videos. Clearly there can be interesting comparisons with Lai and Anders (2021) very recent submission to esurf !

Indeed, this is quite a coincidence! A reference was added to the paper by Lai and Anders (2021).

> The text is short and pithy, so there is space for some extension. There are a few missed opportunities, and some incompleteness in the presentation. In detail I suggest the following improvements:

The manuscript text has been extended in several places. Please see our responses to your specific comments below.


## Specific comments - Text:

> The 1 km resolution of the modelling is clearly important, so it is strange that the first mention is on p.11. Although it is very demanding of computer time, it is still (as admitted) not adequate to represent cirques (averaging of the order of 700 m across). Even stranger, there is no mention of the DEM used (it was SRTM in the 2018 paper). This information should be provided in section 2, p. 3-4.

The model horizontal resolutions of 1 and (for climate sensitivity runs) 2 km is now mentioned in the methods. The input SRTM topography is also referenced in both the methods and the caption of Fig.~2 where it is displayed in the background. Following comments from reviewer #1, the discussion of model limitations regarding the representation of cirque glaciers has also been extended.

> The lateral constraints on valley glaciers are usually covered by a ‘form factor’: how are they handled by this version of the PISM ice sheet model – how has lateral drag been included?

PISM uses a combination of shallow-ice and shallow-shelf stress balances, neither of which includes lateral stresses. Glacier sliding velocities in troughs are governed by (the sliding law and) longitudinal stresses, which is a limitation with respect to higher-order models. Following another comment from reviewer #1 an additional paragraph on basal sliding uncertainties was added, including the following sentence:

    "Lateral stress gradients missing from the shallow-shelf approximation stress balance could also contribute to moderate sliding velocity in narrow troughs (Herman et al., 2011; Egholm et al., 2012a, b; Pedersen et al., 2014)."

> It might be pointed out that the ‘Koppes’ relationship with an exponent of 2.34 is based on 13 data points that are very poorly distributed: in fact, Koppes et al. (2015) go on to drop two outliers and reach an exponent of 2.62.

We clarified in the methods that we use Koppes et al. (2015) erosion law deriving from their full dataset. In addition, this sentence was added in the discussion of the "choice of erosion law":

    "On the other extreme, an even more non-linear erosion law, not tested here, derived from tidewater glaciers but excluding two outliers (ė = 5.3×10^-9 u_b^2.62, Koppes et al., 2015) would result in an even more localized pattern of erosion potential."

> In lines 206-209, the point about trimlines, relating them to time-transgressive erosion, is well taken. But they represent the integrated effect of many phases of glacial erosion (as noted on 223-224), not necessarily just from recessional phases.

Indeed. The sentence was corrected to include "advancing and retreating glaciers" instead of "retreating glaciers".


## - Figures:

> In Fig. 3 is almost impossible to follow the brown lines, unless advancing and retreating parts of lines are distinguished (e.g. by colour). (The ice volume video may help out.)  Also: keep to ‘potential erosion volume’. The pale brown bars show a decline in annual erosion volume with ice volumes over 1.8 cm s.l.e., stronger than is implied in line 110 of the text – it is more than ‘slight’.

Figure 3 was reworked to use different colours for periods of increasing and decreasing ice volume. This actually strikingly highlights the two different regimes, so thank you for the suggestion. The label was changed to 'potential annual erosion volume'. In the text, 'slight' was replaced with a 'general' tendency for slower erosion during periods of extensive glaciation.

> To aid interpretation of Figs 4 a-c and 7 a-d, a corresponding topographic map or hillshade of the Rhine area on the same scale should be provided.

In addition to the aforementioned changes to Fig. 4, a new panel was added for the model final state at 0 ka, revealing the bedrock topography. So Fig. 4 now has one panel during advance (36 ka), one during a maximum stage (24 ka), one during retreat (16 ka), and one nearly ice-free (0 ka).

> Fig. 1c illustrates a very unusual cirque, with a huge lake replacing a very unhealthy convex glacier. Fascinating, but surely a more representative cirque should be used. Actually these three photos are not well integrated with the text (pace lines 191 & 195-198). Lauterbrunnen is an extreme (vertical-sided) trough example, over-used by textbooks.

The figure was moved into the discussion of the "age of the glacial landscape" to become Fig. 8, and is not longer referred to in the intro. The photo of Lauterbrunnental was replaced by one of Bout du Monde in the Giffre Massif, and the caption for the cirque photo now reads: "the unusually deep mountain cirque revealed by the current demise of Chüebodengletscher" (we don't have a much better photo for a high-elevation cirque, and glacial lakes from retreating cirque glaciers are a common occurrence in the Alps these days).

> Fig. 5: The elevation histogram in Fig. 5a could be misleading, as it seems to cover the whole study area, including parts never glacier-covered. It should be limited to areas glacier-covered at the maximum, and preferably supplemented by a histogram for those covered now or at the minimum. The accompanying main graph (5a) relates to areas glacier-covered at each time slice. Re another reviewer’s comment, yes LGM glaciers did reach below 500 m: at L. Garda (67 m?) and the Tagliamento Glacier lobe LGM ice reached below 100 m. An integrated plot of total-cycle potential erosion rate (and volume?) at each altitude, over glacier-covered areas, would be interesting (as an extra Figure): can rates at high altitude, where glacial duration is longer, catch up with those at low altitude?  Probably not, given the concentration of flow down major valleys. Striping above 3000 m, presumably related to low surface area, suggests a switch there to 20 m or 40 m bands would be advisable. Caption; ‘modelled potential erosion rates’?

The figure now includes a histogram of model domain elevations, a histogram of glacier-covered elevations, and a plot of cumulative erosion potential volume per elevation bands of 100 m. The latter shows that, as you suspected, high altitude rapid erosion is largely offset by the limited number of grid cells it concerns. Instead, the bulk of the erosion potential occurs below 2000 m.

To highlight periods when low-elevation is relevant (and address the comment from reviewer #1), we also hatched elevation bands that contain fewer than a hundred ice-covered grid cells for a given time. We also shifted to 100-m elevation bands on the main panel. While some detail is lost, this avoids much of the striping (especially on the newly added contour and hatched pattern), and we find the new plot more readable.

> In Fig. 7, the quantitative contrasts between the ‘Koppes’ law (e) and the others are alarming. If the scales are taken literally, (e) gives potential erosion around 1 m, while (f) and (g) give hundreds of m, in 120 ka. As 120 ka is only a fraction of the Quaternary, hundreds of m seems too much, while 1 m seems very low (0.008 mm a-1 overall). For me, there should be a correct answer between these extremes. The spatial pattern, however, is more important.

Discussion on the magnitude of modelled erosion rates remains somewhat speculative indeed due to the several sources of uncertainties, but the relevant discussion text was extended and reworked:

    "With a total Pleistocene glacial relief on the order of a kilometre (Preusser et al., 2011; Valla et al., 2011), a cumulative glacial erosion for the last glacial cycle in the order of 10 to 100 m can be expected.  However, none of the tested erosion power-laws fall within this range.  Instead, the erosion law calibrated on tidewater glaciers (Koppes et al., 2015) yields cumulative erosion in the Rhine Valley in the orders of metres, while the three erosion laws based on terrestrial glaciers (Humphrey and Raymond, 1994; Herman et al., 2015; Cook et al., 2020}, result in kilometre-scale integrated erosion potential. During the Last Glacial Maximum and much of the last glacial cycle, Alpine paleoglaciers were closer in size, slope (an important parameter as we argue in the next section), and climatic context to the present-day glaciers of Patagonia and the Antarctic Peninsula (Koppes et al., 2015) than to Franz-Joseph Glacier (Herman et al., 2015) and many of the glaciers included in the global compilation by Cook et al., (2020). This may help to explain why the reality appears to fall in-between the tested erosion laws."

> Fig. 8a shows a flat dome at 3000 m for about the first 20 km of the Rhine.  As there are mountains at 3630, 3583 and 3192 m around the sources, it is likely that   there would be steeper ice slopes up to these peaks, giving rather different stresses and erosion potentials. Also are the instabilities in Fig. 8b, near source and terminus, edge effects or related to the 1 km resolution?

This is correct. The "basal drag" quantity plotted on Fig. 8b is the magnitude of a two-component vector: the basal shear stress. The basal shear stress itself strongly depends on surface altitude gradients, but this includes both along-flow slopes visible on the topographic profile of Fig. 8a, and the invisible across-flow slopes. While the upper part of the topographic profile appears smooth, there are indeed steep (bedrock and surface) slopes on either side of the profile in this region. Because the upper part of the valley is narrow, the glacier centre-line fluctuating over time, and the plot interpolated between 1-km grid points, these lateral components enter the computation of the basal shear stress magnitude in the higher reaches.

Second, the activation of sliding also increases basal drag, which explains that basal drag also fluctuates together with the yield stress. This is particularly affecting the lower part of the profiles. Finally, normalization by overburden pressure amplifies all stress variations where ice thickness is small. But due to changes in glacier thickness, it would not be possible to compare different profiles without such normalization.

While we would rather not include such details in the paper, we tried our best to summarise the effect with this additional sentence in the figure caption:

    "Some of the observed basal drag fluctuations in the upper part of the transect result from steep slopes on either side of the narrow valley."

> The three videos are well worth watching  -in fact they clarify some queries arising from the paper. Perhaps they could be captioned in the ‘Video supplement’ paragraph. Some extra information on the third (bedrock altitude) video could point out that there are numerous zero values not shown: the zero geometric mean rates from 2300 to 3000 m around 24 ka otherwise seem to conflict with the numerous positive rates plotted. Zero rates presumably show where ice is frozen to the bed: their altitudinal distribution might be worth discussion in the text. Above 3000 m means are positive, which seems strange.

Well, it seems that you have spend a lot of time looking at our figures and videos so let us thank you again for that. The 'video supplement' paragraph was somewhat extended. The caption of Fig. 5 mentioned "the geometric mean of (non-zero) modelled erosion rates". We found that the "non-zero" has no reason to be and it was removed. Sorry about the confusion and please read on for the long explanation.

First, there are no zero values in the animation. As in the paper's Fig. 5, the animation shows geometric means (i.e. arithmetic means in log-domain), and geometric means can't contain zero values or they would result in a divide-by-zero error (or a log-of-zero error). Both animation panels have a log-scaled x-axis. While some values fall outside of the axis frame, they are very small but not zero.

On the other hand, both Fig. 5 and the animation depict very low values for erosion rates (especially around 24 ka). This is due to the glacier physics embedded in PISM. In particular, the pseudo-plastic sliding law implies that the glacier is sliding everywhere, but that sliding is infinitely small where the basal drag is much smaller than the yield stress, including for instance frozen-bed areas. These tiny sliding velocities yield even tinier erosion rates (due to the power 2.34 in the erosion law). Such values are not really relevant and they are off the colour range on Fig. 5 and off-chart in the animation (respectively lower than 10^-9 and 10^-10 mm a^-1).

The only regions where PISM produces truly zero sliding are the regions of zero surface slopes or zero ice thickness, where the SSA can't be solved. In practice, this only occurs in the latter case: zero ice thickness. This is the kind of values we have previously filtered out. Your comment led us to re-check our calculations. We found that there is no zero-sliding values within the ice-covered area, and thus an ice mask is sufficient to filter out undesirable values and compute the geometric means. Hence "non-zero" was removed from the caption.

To be sure, the non-zero filter has been removed from the script generating companion data (which is used in Fig. 5). This change can be seen here:

    https://github.com/juseg/alps/commit/7d14ec0


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

Thank you for spotting all the above errors! These were corrected.


## Acknowledgements:

> I am grateful for helpful discussions with Iestyn Barr, Jeremy Ely, Matt Tomkins, Pippa Whitehouse, Cristina Balaban and Matt Wiecek.

> - Ian S. Evans, Durham University, U.K.

Thank you again to all of you for taking time to read our work and offer constructive feedback in these troubled times. We hope that you will find our answers satisfactory, apologize for the delay and will soon be submitting a revised and, we believe, improved manuscript including the aforementioned suggested changes.
