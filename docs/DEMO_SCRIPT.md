# Interview Demo Script (8–10 minutes)

1. Register a demo organization and sign in.
2. Upload a short policy document containing harmless test content.
3. Ask a question that is directly answered by the document; inspect citations.
4. Ask an unrelated question; demonstrate abstention.
5. Upload a test document containing a fake API-key-like string; show that ingestion redacts it.
6. Run the synthetic security control suite; explain what each test does and does not prove.
7. Submit an unregistered tool proposal through `/docs`; show server-side blocking.
8. Submit `export_report` as a member; show that role policy blocks it. Explain admin approval path.
9. Inspect traces and usage metrics.
10. Explain the limitations and the next measurable engineering improvements.

Do not claim that the included synthetic suite proves resistance to real-world prompt injection. Explain the distinction between policy-control tests and model-level adversarial benchmarks.
