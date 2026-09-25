# Backend (AI Logic) Module

## Purpose
This is the "brain" of the chatbot. It connects the Frontend, Vector DB, and LLM to provide answers.

## Workflow
1.  **Receive Query**: Frontend sends the user's question.
2.  **Embed**: Convert the question into a vector.
3.  **Search**: Query the Vector DB for the most relevant text chunks.
4.  **Construct Prompt**:
    > "Answer the following question: [User Question] based on the attached context: [Retrieved Text]. At the end of your answer, tell the student: For more details, visit this link: [Retrieved Link]."
5.  **Generate**: Send the prompt to an LLM (GPT-4, Gemini, etc.).
6.  **Respond**: Send the AI's answer back to the Frontend.

## API Endpoints (Planned)
- `POST /api/chat`: Accepts `{ message: string }`, returns `{ reply: string }`.
