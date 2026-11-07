#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OmniLink CLI: Universal Agent Bus Command-Line Tool
"""

import sys
import argparse
from ..core.bus import AgentBus
from ..core.protocol import OmniLinkMessage, MessageType

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

def main():
    parser = argparse.ArgumentParser(description="OmniLink: Universal Inter-Agent Bus")
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # agents list
    subparsers.add_parser("agents", help="List all registered agents and their statuses")

    # send command
    send_parser = subparsers.add_parser("send", help="Send a message to a specific agent")
    send_parser.add_argument("--to", "-t", required=True, help="Destination agent ID (e.g. deepseek, gemini, ollama)")
    send_parser.add_argument("message", nargs="+", help="Message content to send")

    # collab command
    collab_parser = subparsers.add_parser("collab", help="Run dual-agent collaboration loop on a task")
    collab_parser.add_argument("--architect", "-a", default="deepseek", help="Primary thinking agent (default: deepseek)")
    collab_parser.add_argument("--builder", "-b", default="gemini", help="Executing agent (default: gemini)")
    collab_parser.add_argument("task", nargs="+", help="Task description")

    # interactive chat
    chat_parser = subparsers.add_parser("chat", help="Start interactive multi-agent chat")
    chat_parser.add_argument("--agent", "-a", default="deepseek", help="Target agent")

    args = parser.parse_args()
    bus = AgentBus()

    if args.command == "agents":
        print("\n=== الوكلاء المسجلون في شبكة OmniLink ===")
        for agent in bus.list_agents():
            status = "🟢 متاح" if agent["available"] else "⚪ غير متصل"
            print(f"- [{agent['agent_id']}] {agent['name']} -> {status} (القدرات: {', '.join(agent['capabilities'])})")
        print()
        return

    if args.command == "send":
        prompt_text = " ".join(args.message)
        msg = OmniLinkMessage(src_agent="cli_user", dst_agent=args.to, content=prompt_text)
        try:
            res = bus.send(msg)
            print(f"\n[{args.to.upper()}]:\n{res.content}\n")
        except Exception as e:
            sys.stderr.write(f"خطأ أثناء الإرسال: {e}\n")
            sys.exit(1)
        return

    if args.command == "collab":
        task_text = " ".join(args.task)
        print(f"\n🚀 بدء التعاون الثنائي عبر OmniLink للمهمة:\n\"{task_text}\"\n")
        try:
            res = bus.collaborate(task_text, primary_agent=args.architect, secondary_agent=args.builder)
            print(f"--- 🧠 {res['primary']['agent'].upper()} (التخطيط والتحليل) ---")
            print(res['primary']['response'])
            print(f"\n--- ⚡ {res['secondary']['agent'].upper()} (المراجعة والتنفيذ) ---")
            print(res['secondary']['response'])
            print("\n✅ اكتملت جولة التعاون بنجاح.\n")
        except Exception as e:
            sys.stderr.write(f"خطأ أثناء التعاون: {e}\n")
            sys.exit(1)
        return

    if args.command == "chat":
        print(f"\n=== محادثة مباشرة مع الوكيل [{args.agent}] عبر OmniLink ===")
        print("اكتب رسالتك واضغط Enter (أو 'exit' للخروج):")
        while True:
            try:
                user_input = input(f"\n[أنت -> {args.agent}] > ").strip()
                if not user_input:
                    continue
                if user_input.lower() in ["exit", "quit", "خروج"]:
                    break
                msg = OmniLinkMessage(src_agent="cli_user", dst_agent=args.agent, content=user_input)
                res = bus.send(msg)
                print(f"\n[{args.agent.upper()}]:\n{res.content}")
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"[خطأ]: {e}")
        return

    parser.print_help()

if __name__ == "__main__":
    main()
