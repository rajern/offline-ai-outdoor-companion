# Outwise — Product

## What it is

Outwise is an **Offline AI Outdoor Companion** designed to help people handle unexpected situations outdoors when internet access is unavailable.

The first version is a learning-focused MVP that runs fully locally on a PC, while the interface and user experience are designed mobile-first so the concept can later be moved to iOS or Android.

## Problem

When something goes wrong outdoors, useful information may exist in first-aid guides, survival manuals and other resources, but the user may:

- have no internet connection
- not know what information is relevant
- need to combine information from several topics
- need a short, prioritized answer rather than reading a manual

Outwise should turn trusted offline knowledge into useful, situation-specific guidance through natural-language interaction.

## Target user

People travelling, hiking or spending time outdoors where mobile coverage may be unreliable or unavailable.

The initial focus is on situations such as:

- injuries and basic first aid
- getting lost
- cold, exposure and sudden weather changes
- shelter and keeping warm
- water and basic hygiene
- emergency signalling and what to prioritize
- other basic outdoor emergency situations

## Core experience

The user opens Outwise and describes the situation in normal language.

Example:

> I twisted my ankle, I am alone, it is getting dark and I am several kilometres from the car. What should I do?

Outwise should:

1. Understand the situation and ask relevant follow-up questions when necessary.
2. Retrieve relevant information from the local knowledge base.
3. Combine that information into a short, natural and prioritized response.
4. Clearly show the sources supporting the answer.
5. Work without internet access.

The interface should also provide a few simple scenario shortcuts such as:

- I am injured
- I am lost
- I am cold / weather changed
- Other problem

## MVP principles

- Fully functional without internet.
- Local AI model and local knowledge base.
- No account or cloud dependency.
- Answers should be concise, practical and source-grounded.
- Safety-critical information should come from curated sources rather than model memory alone.
- The user should be able to inspect the sources behind an answer.
- The product should clearly communicate uncertainty and when professional or emergency help should be prioritized.
- UI should be designed for a phone-sized screen even though the first MVP runs locally on PC.

## Explicit non-goals for the MVP

Outwise will initially **not** include:

- offline maps
- GPS, compass or other device sensors
- live weather
- satellite communication
- plant, mushroom or animal identification
- camera/image analysis
- Bluetooth mesh communication
- inventory or preparedness management
- user accounts or cloud sync
- model selection by the user
- fine-tuning as a requirement

These can be explored after the core MVP works.

## Product goal

The MVP should demonstrate that a small local language model combined with a curated local knowledge base can provide useful, source-grounded outdoor guidance entirely offline.

If the result proves useful, the same concept can later be adapted into a native mobile application and expanded with device tools such as location, compass and other offline capabilities.