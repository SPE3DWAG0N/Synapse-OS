"use client";

import React, { useState, useRef, useEffect } from "react";
import ReactMarkdown from "react-markdown";
import styles from "./Chat.module.css";
import Integrations from "./Integrations";

interface Message {
  id: string;
  role: "user" | "ai";
  content: string;
}

interface Conversation {
  id: number;
  title: string;
}

export default function Chat() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeConvId, setActiveConvId] = useState<number | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [showIntegrations, setShowIntegrations] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const [attachedFiles, setAttachedFiles] = useState<string[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Load conversations on mount
  useEffect(() => {
    fetchConversations();
  }, []);

  // Fetch messages when active conversation changes
  useEffect(() => {
    if (activeConvId) {
      fetchConversationMessages(activeConvId);
    } else {
      setMessages([{
        id: "1",
        role: "ai",
        content: "Hello! I am Synapse OS. How can I help you today?"
      }]);
    }
  }, [activeConvId]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  const fetchConversations = async () => {
    try {
      const res = await fetch("http://localhost:8000/api/conversations/");
      const data = await res.json();
      setConversations(data);
    } catch (err) {
      console.error(err);
    }
  };

  const fetchConversationMessages = async (id: number) => {
    try {
      const res = await fetch(`http://localhost:8000/api/conversations/${id}`);
      const data = await res.json();
      setMessages(data.messages);
    } catch (err) {
      console.error(err);
    }
  };

  const startNewChat = async () => {
    try {
      const res = await fetch("http://localhost:8000/api/conversations/", { method: "POST" });
      const newConv = await res.json();
      await fetchConversations();
      setActiveConvId(newConv.id);
    } catch (err) {
      console.error(err);
      setActiveConvId(null);
    }
  };

  const deleteConversation = async (e: React.MouseEvent, id: number) => {
    e.stopPropagation();
    if (!window.confirm("Are you sure you want to delete this chat?")) return;
    
    try {
      const res = await fetch(`http://localhost:8000/api/conversations/${id}`, { method: "DELETE" });
      if (res.ok) {
        setConversations(prev => prev.filter(c => c.id !== id));
        if (activeConvId === id) {
          setActiveConvId(null);
          setMessages([{
            id: "1",
            role: "ai",
            content: "Hello! I am Synapse OS. How can I help you today?"
          }]);
        }
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: input.trim()
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      const payload: any = { query: userMessage.content };
      if (activeConvId) {
        payload.conversation_id = activeConvId;
      }

      const res = await fetch("http://localhost:8000/chat/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload)
      });

      if (!res.ok) throw new Error("Failed to fetch response");
      
      setIsLoading(false); // Stop main loading, start streaming

      const reader = res.body?.getReader();
      const decoder = new TextDecoder("utf-8");
      
      if (!reader) throw new Error("No reader");

      let currentConvId = activeConvId;
      
      const aiMsgId = (Date.now() + 1).toString();
      setMessages((prev) => [...prev, { id: aiMsgId, role: "ai", content: "" }]);

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split("\n\n");
        
        for (const line of lines) {
          if (line.startsWith("data: ")) {
            const dataStr = line.replace("data: ", "");
            if (!dataStr) continue;
            
            try {
              const data = JSON.parse(dataStr);
              if (data.status === "start" && data.conversation_id && !currentConvId) {
                currentConvId = data.conversation_id;
                fetchConversations(); // Update sidebar immediately
                // Note: We defer setActiveConvId until after the stream to prevent a race condition 
                // where the useEffect fetches DB messages and wipes out the currently streaming AI bubble.
              } else if (data.text) {
                setMessages((prev) => 
                  prev.map(msg => 
                    msg.id === aiMsgId ? { ...msg, content: msg.content + data.text } : msg
                  )
                );
              }
            } catch (e) {
              console.error("Error parsing JSON:", e);
            }
          }
        }
      }
      
      // Now that the stream is completely finished, it is safe to set the active conversation ID.
      // This will trigger a re-fetch of the messages from the DB, ensuring everything is in sync.
      if (!activeConvId && currentConvId) {
        setActiveConvId(currentConvId);
      }
    } catch (error) {
      console.error(error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "ai",
        content: "Sorry, I encountered an error connecting to the backend. Please ensure the FastAPI server is running."
      };
      setMessages((prev) => [...prev, errorMessage]);
      setIsLoading(false);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };
  
  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };
  
  const handleDrop = async (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    
    const files = Array.from(e.dataTransfer.files);
    for (const file of files) {
      if (file.name.endsWith('.pdf') || file.name.endsWith('.txt') || file.name.endsWith('.md')) {
        const formData = new FormData();
        formData.append("file", file);
        
        try {
          setAttachedFiles(prev => [...prev, `Uploading ${file.name}...`]);
          
          const res = await fetch("http://localhost:8000/api/integrations/documents/upload", {
            method: "POST",
            body: formData
          });
          
          if (res.ok) {
            setAttachedFiles(prev => {
              const newArr = [...prev];
              newArr[newArr.length - 1] = file.name;
              return newArr;
            });
          } else {
             setAttachedFiles(prev => prev.filter(f => !f.startsWith("Uploading")));
          }
        } catch (err) {
          console.error(err);
          setAttachedFiles(prev => prev.filter(f => !f.startsWith("Uploading")));
        }
      }
    }
  };

  return (
    <div className={styles.layout}>
      {/* Sidebar for Conversations */}
      <div className={styles.sidebar}>
        <div className={styles.sidebarHeader}>
          <div className={styles.logo}>Synapse OS</div>
          <button className={styles.newChatButton} onClick={startNewChat} title="New Chat">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M12 5v14M5 12h14"></path>
            </svg>
          </button>
        </div>
        
        <div className={styles.conversationsList}>
          {conversations.map(conv => (
            <div 
              key={conv.id} 
              className={`${styles.conversationItem} ${activeConvId === conv.id ? styles.activeConversation : ''}`}
              onClick={() => setActiveConvId(conv.id)}
            >
              <span className={styles.conversationTitle}>{conv.title}</span>
              <button 
                className={styles.deleteButton} 
                onClick={(e) => deleteConversation(e, conv.id)}
                title="Delete Chat"
              >
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M3 6h18"></path><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Main Chat Area */}
      <div 
        className={styles.chatContainer}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        {isDragging && (
          <div className={styles.dragOverlay}>
            <div className={styles.dragMessage}>Drop files here to add to context</div>
          </div>
        )}
        
        <div className={styles.header}>
          <h2 className={styles.title}>
            {activeConvId ? conversations.find(c => c.id === activeConvId)?.title : "New Chat"}
          </h2>
          <button 
            className={styles.settingsButton}
            onClick={() => setShowIntegrations(!showIntegrations)}
          >
            {showIntegrations ? "Close Integrations" : "Data Integrations"}
          </button>
        </div>
        
        <div className={styles.messagesArea}>
          {messages.length === 1 && !activeConvId ? (
            <div className={styles.emptyState}>
              <div className={styles.emptyStateIcon}>🧠</div>
              <h2>Welcome to Synapse OS</h2>
              <p>Your AI-powered second brain. What would you like to explore today?</p>
              <div className={styles.suggestionChips}>
                <button onClick={() => setInput("Summarize my recent notes")}>Summarize my notes</button>
                <button onClick={() => setInput("What are my action items?")}>Find action items</button>
                <button onClick={() => setInput("Explain the system architecture")}>Explain architecture</button>
              </div>
            </div>
          ) : (
            messages.map((msg) => (
              <div 
                key={msg.id} 
                className={`${styles.messageWrapper} ${msg.role === "user" ? styles.messageUser : styles.messageAi}`}
              >
                <div 
                  className={`${styles.messageBubble} ${msg.role === "user" ? styles.messageBubbleUser : styles.messageBubbleAi}`}
                >
                  {msg.role === "user" ? (
                    msg.content
                  ) : (
                    <div className={styles.aiMessageContainer}>
                      <ReactMarkdown>{msg.content}</ReactMarkdown>
                      <button 
                        className={styles.copyButton}
                        onClick={() => navigator.clipboard.writeText(msg.content)}
                        title="Copy message"
                      >
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
                      </button>
                    </div>
                  )}
                </div>
              </div>
            ))
          )}
          
          {isLoading && (
            <div className={`${styles.messageWrapper} ${styles.messageAi}`}>
              <div className={`${styles.messageBubble} ${styles.messageBubbleAi}`}>
                <div className={styles.loadingIndicator}>
                  <div className={styles.dot}></div>
                  <div className={styles.dot}></div>
                  <div className={styles.dot}></div>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
        
        <div className={styles.inputWrapper}>
          {attachedFiles.length > 0 && (
            <div className={styles.attachedFilesContainer}>
              {attachedFiles.map((file, i) => (
                 <div key={i} className={styles.attachedPill}>
                   <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"></path></svg>
                   {file}
                 </div>
              ))}
            </div>
          )}
          <form onSubmit={handleSubmit} className={styles.inputForm}>
            <textarea
              value={input}
              onChange={(e) => {
                setInput(e.target.value);
                e.target.style.height = 'inherit';
                e.target.style.height = `${Math.min(e.target.scrollHeight, 200)}px`;
              }}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSubmit(e);
                }
              }}
              placeholder="Ask your second brain..."
              className={styles.inputField}
              disabled={isLoading}
              autoFocus
              rows={1}
            />
            <button 
              type="submit" 
              className={styles.sendButton}
              disabled={!input.trim() || isLoading}
            >
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <line x1="22" y1="2" x2="11" y2="13"></line>
                <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
              </svg>
            </button>
          </form>
        </div>
        
        {showIntegrations && (
          <Integrations />
        )}
      </div>
    </div>
  );
}
