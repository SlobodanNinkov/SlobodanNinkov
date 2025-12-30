---
layout: post
title: "Field Testing IoT Devices: A Practical Checklist"
subtitle: 
comments: true
mathjax: true
author: Slobodan Ninkov
---

After running dozens of IoT field tests, these are the things that actually matter. Most come from mistakes.  

IoT device initial field testing is a special moment in the product lifecycle. During this phase, the team receives brutal, reality-based feedback on technical decisions made during development.  
  
The short list below captures practical know‑how that will hopefully save you time. It originates from multiple discussions with peers about how to run a field test.  
  
These lists are written from the perspective of a team lead responsible for successful test execution.  
  
# Preparations for the trip  
  * Develop a test plan. What are you testing? What outcomes do you expect?  
  * Get the budget approved, or scope the test so it can be self‑financed by the team lead.  
  * Check legal constraints (e.g., drone flight restrictions, permitted frequencies, spectrum licenses).  
  * Choose the test location and, if possible, contact local responsible parties.  
  * Review the location on maps; understand access roads, nearest houses, gas stations, and shops.  
  * Arrange transportation.  
  * Arrange food and water.  
  * Prepare a parts checklist. Double‑check everything; assume you’ll forget something.  
  * Visualize the test from start to the end, missing cables, faulty cables, etc.  
  * Bring repair and test tools.  
  * Bring spare devices if possible. Devices tend to fail once you’re 50+ km from the lab.  
  * Charge all batteries or bring a generator. If bringing a generator, don’t forget fuel and a power inverter (DC-to-AC).  
  * Prepare sun protection: shade, hats, sunscreen.  
  * Avoid food that could upset your stomach the day before and during testing.  
  * Brief your superiors on the plan so they’re aware of the day’s activities.  
  * Keep phone numbers for your boss and legal on hand; prepare a brief explanation in case law enforcement inquires.  
  * Brief all team members on what you’ll do, why, and how—avoid on‑site debates.  
  * Plan data collection methods and formats.  
  * Bring cables, spare cables, and spare tested cables.  
  * Wear appropriate workwear and sturdy shoes.  

# During the testing  
  * Prioritize safety.  
  * Ensure every team member understands their responsibilities.  
  * Double‑check time synchronization across all relevant clocks/devices.  
  * Prepare spreadsheets/templates for manual data collection.  
  * Enable photo timestamps/metadata on phones and verify it works.  
  * Execute the test plan and collect all data. Double‑check entries and logs.  
  * Expect reduced cognitive capacity under field stress, especially in early tests—keep procedures simple, explicit, and straightforward.  
  * Field‑savvy team members (e.g., with military experience) can be invaluable, particularly when technically inclined.  
  * Duplicate the directory with test results to a second location on the computer.  
  * Include at least one first‑time user (who matches the user profile); observe for priceless UX insights.  

# After the test (same day)  
  * Pack up everything and double‑check you’ve got it all.  
  * Clean the area; use available trash cans or carry waste out. Do not litter.  
  * Debrief during the return trip. Tired feedback is candid—capture it.  
  * Write a short day summary: what went right, what went wrong, improvements, device issues, and any observations. Save it with the test results.  
  * Copy all phone images to the test results directory.  
  * Back up the test results directory to the company servers.  
  * Inform your superior that the test is complete; share a summary and commit to a full report tomorrow.  
  * Confirm that no one was left in the field.  

# The day after testing  
  * Write the full report based on data and feedback.  
  * Review results with stakeholders (team, product owner/manager, etc.).  
  * Submit receipts for food and transportation to accounting.  

# Notes and optional enhancements  
  * Add a preflight “Go/No‑Go” checklist: weather, permits in hand, site access confirmed, critical spares present.  
  * Time sync: specify a standard (e.g., NTP server, GPS time) and require a sync check at start and mid‑test.  
  * Data schema: define exact filenames, metadata fields, and folder structure before the trip to avoid chaos later.  
  * Risk register: list top 5 risks (power, comms, interference, mechanical, environmental) with mitigations.  
  * Incident protocol: who leads, who contacts legal/PR, what to say, what not to say.  
  * EHS specifics: PPE list, heat/cold plans, first‑aid kit, nearest emergency room, site hazard brief.  
  * RF/EMI: if applicable, bring a spectrum snapshot tool and document ambient conditions pre/post test.  
