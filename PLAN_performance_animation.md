# Plan: Living Poster v3, next performance and animation pass (1 Nov 2026)

## Where it stands
- Already done and live:
  - Lens frame over the cytosol: ~80 → ~12–15 ms of script and style.
  - Particles are batched and the micro layer is no longer re-cloned.
  - The sheet stops painting under the cover.
  - The `?fps` readout works.
- Built today, in the scratchpad (`C:\Users\aitor\AppData\Local\Temp\claude\C--Users-aitor-Downloads-BIOCELL-POSTER\07e647a1-84d3-4074-802a-85e46c89e216\scratchpad\`):
  - `ab.mjs`: drives a separate Chrome over DevTools. It traces per-frame script, style, layout, paint, raster and GPU time and A/B-tests variants in one session.
  - `scen.py`: lists the lens spots and every scene at 20/55/85 %.
  - `closecdp.mjs`: closes that Chrome by port.
- First findings:
  - Once warm, the gallery is cheap: ~1 ms of script per frame, hundreds of fps uncapped.
  - The worst slowness found so far is the first seconds after load, while the 4331×3543 plate, blur and cover JPEGs decode. One cold run showed 26 ms of raster and 45 ms of GPU time per frame (22 fps).
  - The camera's hand-held drift and the light sweep force a full-sheet repaint every frame. Switching both off raised throughput ~1.5×.
- A full lens and scene sweep was started but didn't finish before the deadline. Its results are not in yet.

## Next steps (in order)
1. **Finish the measurement.** Re-run `node ab.mjs "" "$(python scen.py scenes)" 1 3` with `SETTLE=1500`. Rank scenes and lens spots by raster + GPU time; the slowest five are the targets.
2. **Load-time jank.**
   - Decode the plate, blur, cover and actor images before the loading screen lifts (`img.decode()` on each href).
   - Keep "the paper is drying…" up until they're decoded.
   - Ship a 2166-px plate for the gallery view and attach the full 4331-px one only when zoomed in (the tiles already do this for close-ups).
3. **Paint the sheet less often.**
   - Drift: snap the hand-held drift to slow steps when the camera is otherwise still, or move it into a CSS transform on `#stage` (composited, no re-raster).
   - Sweep: draw the sweep as one composited HTML overlay rather than an SVG ellipse inside the clipped world.
   - Check visually that both look the same.
4. **Filters.**
   - Lens flow: measure feTurbulence + feDisplacementMap. If it is expensive, pre-render the noise once to a small image tile and feed it to feDisplacementMap via `feImage`. That keeps the look and drops the per-frame noise generation.
   - Wobble filters (`wobRegion` and the actor filters): do the same.
   - Measure `mix-blend-mode: multiply` on `L_wash`. If it is costly, swap it for a pre-multiplied fill colour.
5. **Animation quality, once frames are steady.**
   - Ease every scene's camera with critically damped springs instead of fixed-duration cubic curves, so interrupting with → or ← never jumps.
   - Give actor motion a small follow-through (overshoot and settle) on arrivals.
   - Under the lens:
     - Brownian ions with velocity persistence.
     - Motors that pause and step (8 nm steps, visibly hand-over-hand).
     - Vesicle fusion that flattens into the membrane.
   - Rate-independent timing everywhere: any per-frame `lerp(x, y, 0.05)` becomes `1 - exp(-dt/τ)`.
     - Known cases: `Loupe.update` flow amp and lens k, which currently run faster on fast screens.
6. **Verify.**
   - Re-run the sweep: the before/after table goes into `CHANGELOG_review03.md`.
   - Screenshot every scene at three times and the lens at six spots against the current build, to check nothing changed in look.
   - Confirm 0 console errors.
   - Check `?fps` in your own browser.

## Notes
- The temporary `App.noDrift` probe switch has been removed from `js/main.js`. No other code changed today.
