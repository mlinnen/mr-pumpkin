# Session Log — Issue #21: Rolling Eyes Animation

**Date:** 2026-02-22  
**Requested by:** Mike Linnen  
**Who worked:** Ekko (Graphics Dev), Vi (Backend Dev)  

## What They Did

Enhanced rolling eyes animation to start from current pupil position and rotate 360° before returning to starting angle.

## Key Decision

**Capture-Animate-Restore Pattern:** Maintains smooth composability with other animations.

The implementation captures the current pupil position at the start of the animation, rotates through a full 360° circle, and restores to the original position. This pattern ensures the rolling eyes animation composes cleanly with other concurrent animations (blink, expression transitions) without state conflicts or visual glitches.

## Pattern

This follows the same orthogonal animation model established by the blink animation system — a temporary animation overlay that preserves and restores the underlying expression state without disrupting the main state machine.
