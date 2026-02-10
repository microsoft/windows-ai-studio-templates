# Copyright (c) Microsoft. All rights reserved.

import asyncio
from dataclasses import dataclass
from typing import Any

from agent_framework import (
    ChatMessage,
    WorkflowBuilder,
    WorkflowContext,
    executor,
)
from typing_extensions import Never

"""
Sample: Conditional routing with deterministic mock data (no AI)

What this sample is:
- A minimal decision workflow that classifies an inbound email as spam or not spam using
  keyword-based detection, then routes to the appropriate handler.

Purpose:
- Show how to attach boolean edge conditions that inspect executor output.
- Demonstrate deterministic routing with mock data instead of AI agents.
- Illustrate how to transform one executor's result into input for a downstream executor.

High level flow:
1) spam_detector reads an email and returns a DetectionResult using keyword matching.
2) If not spam, we forward the email to draft_reply, which produces a canned professional response.
3) If spam, we short-circuit to a spam handler that yields a spam notice as workflow output.

Output:
- The final workflow output is printed to stdout, either with a drafted reply or a spam notice.
"""

# ----- Spam keywords used for deterministic detection -----
SPAM_KEYWORDS = [
    "click here",
    "won",
    "prize",
    "free money",
    "act now",
    "limited time",
    "congratulations",
    "claim your",
    "lottery",
    "urgent",
]


@dataclass
class DetectionResult:
    """Represents the result of spam detection."""

    is_spam: bool
    reason: str
    email_content: str


@dataclass
class EmailResponse:
    """Represents the response from the email drafter."""

    response: str


def get_condition(expected_result: bool):
    """Create a condition callable that routes based on DetectionResult.is_spam."""

    def condition(message: Any) -> bool:
        if not isinstance(message, DetectionResult):
            return True
        return message.is_spam == expected_result

    return condition


@executor(id="spam_detector")
async def spam_detector(messages: list[ChatMessage], ctx: WorkflowContext[DetectionResult]) -> None:
    """Deterministic spam detection using keyword matching."""
    email_text = messages[-1].text if messages else ""
    lower = email_text.lower()

    matched = [kw for kw in SPAM_KEYWORDS if kw in lower]

    if matched:
        result = DetectionResult(
            is_spam=True,
            reason=f"Matched spam keywords: {', '.join(matched)}",
            email_content=email_text,
        )
    else:
        result = DetectionResult(
            is_spam=False,
            reason="No spam keywords detected.",
            email_content=email_text,
        )

    await ctx.send_message(result)


@executor(id="draft_reply")
async def draft_reply(detection: DetectionResult, ctx: WorkflowContext[EmailResponse]) -> None:
    """Produce a deterministic mock reply to the original email."""
    mock_reply = (
        "Thank you for your email. I have reviewed the contents and will follow up "
        "with the appropriate next steps shortly.\n\n"
        "Best regards,\n"
        "Auto-Responder"
    )
    await ctx.send_message(EmailResponse(response=mock_reply))


@executor(id="send_email")
async def handle_email_response(response: EmailResponse, ctx: WorkflowContext[Never, str]) -> None:
    """Yield the drafted reply as the final workflow output."""
    await ctx.yield_output(f"Email sent:\n{response.response}")


@executor(id="handle_spam")
async def handle_spam_classifier_response(detection: DetectionResult, ctx: WorkflowContext[Never, str]) -> None:
    """Yield a spam notice as the final workflow output."""
    if detection.is_spam:
        await ctx.yield_output(f"Email marked as spam: {detection.reason}")
    else:
        raise RuntimeError("This executor should only handle spam messages.")


async def main() -> None:
    import sys

    # Build the workflow graph.
    # Start at the spam detector.
    # If not spam -> draft_reply -> send_email
    # If spam -> handle_spam
    workflow = (
        WorkflowBuilder(name="EdgeConditionsWorkflow")
        .register_executor(lambda: spam_detector, name="spam_detector")
        .register_executor(lambda: draft_reply, name="draft_reply")
        .register_executor(lambda: handle_email_response, name="send_email")
        .register_executor(lambda: handle_spam_classifier_response, name="handle_spam")
        # Not-spam path: detection -> draft reply -> send email
        .add_edge("spam_detector", "draft_reply", condition=get_condition(False))
        .add_edge("draft_reply", "send_email")
        # Spam path: detection -> spam handler
        .add_edge("spam_detector", "handle_spam", condition=get_condition(True))
        .set_start_executor("spam_detector")
        .build()
    )

    if "--cli" in sys.argv:
        # CLI mode: test with two sample emails
        emails = [
            ("SPAM", "you won 10000000000 dollars!!! Click here to claim your prize."),
            ("NOT SPAM", "Hi Sarah, I wanted to follow up on our team meeting this morning."),
        ]
        for label, email in emails:
            print(f"\n--- Testing [{label}] ---")
            print(f"Input: {email}")
            request = [ChatMessage("user", text=email)]
            async for event in workflow.run_stream(request):
                print(event)
    else:
        # Server mode (default) - run as HTTP server for debugging with Agent Inspector
        print("Starting workflow agent HTTP server...")
        from azure.ai.agentserver.agentframework import from_agent_framework
        from starlette.middleware.cors import CORSMiddleware

        agent = workflow.as_agent(name="EdgeConditionsWorkflow")
        server = from_agent_framework(agent)
        server.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        await server.run_async()

    """
    Sample Output:

    --- Testing [SPAM] ---
    Input: you won 10000000000 dollars!!! Click here to claim your prize.
    Workflow output: Email marked as spam: Matched spam keywords: click here, won, prize, claim your

    --- Testing [NOT SPAM] ---
    Input: Hi Sarah, I wanted to follow up on our team meeting this morning.
    Workflow output: Email sent:
    Thank you for your email. I have reviewed the contents and will follow up
    with the appropriate next steps shortly.

    Best regards,
    Auto-Responder
    """


if __name__ == "__main__":
    asyncio.run(main())