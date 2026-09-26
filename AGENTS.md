# Agent Guide

- When documenting or validating a web service UI or frontend from Termux, read [the real-browser validation note](notes/2026-09-26-termux-real-browser-validation.md) before choosing tools. Identify the product's target browser and viewport separately from the Android development host.
- Run a real user flow in Firefox/WebDriver, inspect its screenshot, and read back any exported file relevant to the task. Record the URL, browser engine, CSS viewport, assertions, and remaining cross-browser coverage. Keep the target project's existing CI browser checks.
