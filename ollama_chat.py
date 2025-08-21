#!/usr/bin/env python3
"""與 Ollama 互動對話系統"""

import requests
import json
import sys
from datetime import datetime

class OllamaChat:
    def __init__(self, model="gpt-oss:latest"):
        self.ollama_url = "http://192.168.53.254:11434"
        self.model = model
        self.conversation_history = []
        
    def chat(self, user_input):
        """發送訊息給 Ollama 並獲取回應"""
        # 加入使用者訊息到對話歷史
        self.conversation_history.append({
            "role": "user",
            "content": user_input
        })
        
        try:
            response = requests.post(
                f"{self.ollama_url}/api/chat",
                json={
                    "model": self.model,
                    "messages": self.conversation_history,
                    "stream": False
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                assistant_message = result.get('message', {}).get('content', '無回應')
                
                # 加入助手回應到對話歷史
                self.conversation_history.append({
                    "role": "assistant",
                    "content": assistant_message
                })
                
                return assistant_message
            else:
                return f"錯誤: HTTP {response.status_code}"
                
        except Exception as e:
            return f"連線錯誤: {str(e)}"
    
    def clear_history(self):
        """清除對話歷史"""
        self.conversation_history = []
        print("對話歷史已清除")
    
    def save_conversation(self):
        """儲存對話記錄"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"conversation_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({
                "model": self.model,
                "timestamp": timestamp,
                "messages": self.conversation_history
            }, f, ensure_ascii=False, indent=2)
        
        print(f"對話已儲存到: {filename}")

def main():
    print("🤖 Ollama 對話系統")
    print("="*50)
    print("可用指令:")
    print("  /quit 或 /exit - 結束對話")
    print("  /clear - 清除對話歷史")
    print("  /save - 儲存對話記錄")
    print("  /model - 切換模型")
    print("="*50)
    
    chat = OllamaChat()
    print(f"使用模型: {chat.model}")
    print("\n開始對話...")
    
    while True:
        try:
            # 獲取使用者輸入
            user_input = input("\n您: ").strip()
            
            # 處理特殊指令
            if user_input.lower() in ['/quit', '/exit']:
                print("再見！")
                break
            elif user_input.lower() == '/clear':
                chat.clear_history()
                continue
            elif user_input.lower() == '/save':
                chat.save_conversation()
                continue
            elif user_input.lower() == '/model':
                print("\n可用模型:")
                print("1. gpt-oss:latest")
                print("2. llama3:70b")
                print("3. gemma3:12b")
                print("4. gemma3:27b")
                choice = input("選擇模型 (1-4): ")
                models = ["gpt-oss:latest", "llama3:70b", "gemma3:12b", "gemma3:27b"]
                if choice.isdigit() and 1 <= int(choice) <= 4:
                    chat.model = models[int(choice)-1]
                    print(f"已切換到: {chat.model}")
                continue
            
            if not user_input:
                continue
            
            # 發送訊息並獲取回應
            print("\nOllama: ", end="", flush=True)
            response = chat.chat(user_input)
            print(response)
            
        except KeyboardInterrupt:
            print("\n\n中斷對話")
            break
        except Exception as e:
            print(f"\n錯誤: {str(e)}")

if __name__ == "__main__":
    main()