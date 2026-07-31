"use client";

import React, { useState, useRef } from 'react';
import styles from './Integrations.module.css';

export default function Integrations() {
  const [activeTab, setActiveTab] = useState<'github' | 'youtube' | 'email' | 'upload'>('github');
  const [isSyncing, setIsSyncing] = useState(false);
  const [message, setMessage] = useState<{text: string, type: 'success' | 'error'} | null>(null);

  // GitHub state
  const [repo, setRepo] = useState("");
  const [token, setToken] = useState("");

  // YouTube state
  const [youtubeUrl, setYoutubeUrl] = useState("");

  // Email state
  const [imapServer, setImapServer] = useState("imap.gmail.com");
  const [emailAddress, setEmailAddress] = useState("");
  const [appPassword, setAppPassword] = useState("");

  // Upload refs
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleSync = async (url: string, payload?: any, isFormData: boolean = false) => {
    setIsSyncing(true);
    setMessage(null);

    try {
      const options: RequestInit = { method: "POST" };
      if (isFormData) {
        options.body = payload; // FormData
      } else {
        options.headers = { "Content-Type": "application/json" };
        options.body = JSON.stringify(payload);
      }

      const res = await fetch(`http://localhost:8000/api/integrations/${url}`, options);
      const data = await res.json();
      
      if (!res.ok) throw new Error(data.detail || "Failed to sync");

      setMessage({ text: data.message, type: 'success' });
      
      // Clear fields
      if (url === 'github') { setRepo(""); setToken(""); }
      if (url === 'youtube') { setYoutubeUrl(""); }
      if (url === 'email') { setAppPassword(""); }
      if (fileInputRef.current) fileInputRef.current.value = "";

    } catch (err: any) {
      setMessage({ text: err.message, type: 'error' });
    } finally {
      setIsSyncing(false);
    }
  };

  const onFileUpload = (e: React.ChangeEvent<HTMLInputElement>, type: 'calendar' | 'document') => {
    const file = e.target.files?.[0];
    if (!file) return;
    
    const formData = new FormData();
    formData.append("file", file);
    
    const endpoint = type === 'calendar' ? 'calendar' : 'documents/upload';
    handleSync(endpoint, formData, true);
  };

  return (
    <div className={styles.panel}>
      <div>
        <h2 className={styles.title}>Data Sources</h2>
        <p className={styles.description}>Connect your digital life to Synapse OS.</p>
      </div>

      <div className={styles.tabs}>
        <button className={`${styles.tab} ${activeTab === 'github' ? styles.activeTab : ''}`} onClick={() => setActiveTab('github')}>GitHub</button>
        <button className={`${styles.tab} ${activeTab === 'youtube' ? styles.activeTab : ''}`} onClick={() => setActiveTab('youtube')}>YouTube</button>
        <button className={`${styles.tab} ${activeTab === 'email' ? styles.activeTab : ''}`} onClick={() => setActiveTab('email')}>Email</button>
        <button className={`${styles.tab} ${activeTab === 'upload' ? styles.activeTab : ''}`} onClick={() => setActiveTab('upload')}>Upload</button>
      </div>

      <div className={styles.integrationCard}>
        {activeTab === 'github' && (
          <form onSubmit={(e) => { e.preventDefault(); handleSync('github', { repository_name: repo, github_token: token }); }} style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            <div className={styles.inputGroup}>
              <label className={styles.label}>Repository (owner/repo)</label>
              <input type="text" className={styles.input} value={repo} onChange={(e) => setRepo(e.target.value)} disabled={isSyncing} />
            </div>
            <div className={styles.inputGroup}>
              <label className={styles.label}>Personal Access Token</label>
              <input type="password" className={styles.input} value={token} onChange={(e) => setToken(e.target.value)} disabled={isSyncing} />
            </div>
            <button type="submit" className={styles.syncButton} disabled={!repo || !token || isSyncing}>
              {isSyncing ? "Syncing..." : "Sync GitHub"}
            </button>
          </form>
        )}

        {activeTab === 'youtube' && (
          <form onSubmit={(e) => { e.preventDefault(); handleSync('youtube', { youtube_url: youtubeUrl }); }} style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            <div className={styles.inputGroup}>
              <label className={styles.label}>YouTube Video URL</label>
              <input type="url" className={styles.input} placeholder="https://youtube.com/watch?v=..." value={youtubeUrl} onChange={(e) => setYoutubeUrl(e.target.value)} disabled={isSyncing} />
            </div>
            <button type="submit" className={styles.syncButton} disabled={!youtubeUrl || isSyncing}>
              {isSyncing ? "Syncing..." : "Sync Transcript"}
            </button>
          </form>
        )}

        {activeTab === 'email' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
            <div style={{ padding: '16px', backgroundColor: 'rgba(255, 255, 255, 0.05)', borderRadius: '8px', border: '1px solid rgba(255, 255, 255, 0.1)' }}>
              <h3 style={{ margin: '0 0 8px 0', fontSize: '1.1rem', color: '#fff' }}>Option 1: Local Outlook Agent (Recommended for Windows)</h3>
              <p style={{ margin: '0 0 16px 0', fontSize: '0.9rem', color: '#ccc', lineHeight: '1.4' }}>
                If you use the Microsoft Outlook desktop app on Windows, you can sync your emails securely without any passwords or OAuth setup using our local agent script.
              </p>
              <div style={{ backgroundColor: '#000', padding: '12px', borderRadius: '4px', fontFamily: 'monospace', fontSize: '0.85rem', color: '#0f0' }}>
                1. Open a terminal on your Windows machine<br/>
                2. pip install pywin32 requests<br/>
                3. python backend/scripts/local_outlook_agent.py
              </div>
            </div>

            <div style={{ padding: '16px', backgroundColor: 'rgba(255, 255, 255, 0.05)', borderRadius: '8px', border: '1px solid rgba(255, 255, 255, 0.1)' }}>
              <h3 style={{ margin: '0 0 16px 0', fontSize: '1.1rem', color: '#fff' }}>Option 2: IMAP Server (Coming Soon)</h3>
              <form onSubmit={(e) => { e.preventDefault(); handleSync('email', { imap_server: imapServer, email_address: emailAddress, app_password: appPassword }); }} style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                <div className={styles.inputGroup}>
                  <label className={styles.label}>IMAP Server</label>
                  <input type="text" className={styles.input} value={imapServer} onChange={(e) => setImapServer(e.target.value)} disabled={isSyncing} />
                </div>
                <div className={styles.inputGroup}>
                  <label className={styles.label}>Email Address</label>
                  <input type="email" className={styles.input} value={emailAddress} onChange={(e) => setEmailAddress(e.target.value)} disabled={isSyncing} />
                </div>
                <div className={styles.inputGroup}>
                  <label className={styles.label}>App Password</label>
                  <input type="password" className={styles.input} value={appPassword} onChange={(e) => setAppPassword(e.target.value)} disabled={isSyncing} />
                </div>
                <button type="submit" className={styles.syncButton} disabled={!emailAddress || !appPassword || isSyncing}>
                  {isSyncing ? "Syncing..." : "Sync Recent Emails"}
                </button>
              </form>
            </div>
          </div>
        )}

        {activeTab === 'upload' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            <div className={styles.inputGroup}>
              <label className={styles.label}>Upload Calendar (.ics)</label>
              <input type="file" accept=".ics" className={styles.input} onChange={(e) => onFileUpload(e, 'calendar')} disabled={isSyncing} ref={fileInputRef} />
            </div>
            <div className={styles.inputGroup}>
              <label className={styles.label}>Upload Document (PDF, TXT, MD)</label>
              <input type="file" accept=".pdf,.txt,.md" className={styles.input} onChange={(e) => onFileUpload(e, 'document')} disabled={isSyncing} ref={fileInputRef} />
            </div>
            {isSyncing && <div className={styles.loadingText}>Uploading & Processing...</div>}
          </div>
        )}

        {message && (
          <div className={`${styles.message} ${message.type === 'success' ? styles.success : styles.error}`}>
            {message.text}
          </div>
        )}
      </div>
    </div>
  );
}
