"use client";

import React, { useState, useRef } from "react";
import { UploadCloud, File as FileIcon, X, Download, Loader2, FileBraces } from "lucide-react";
import NavbarFloating from "@/components/ruixen/navbar-floating";
import ButtonCopy from "@/components/ruixen/button-copy";

export default function Home() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [urlInput, setUrlInput] = useState<string>("");
  const [isDragging, setIsDragging] = useState(false);
  const [isConverting, setIsConverting] = useState(false);
  const [markdownOutput, setMarkdownOutput] = useState<string>("");
  const [error, setError] = useState<string>("");
  
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      setSelectedFile(e.dataTransfer.files[0]);
      setError("");
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setSelectedFile(e.target.files[0]);
      setError("");
    }
  };

  const handleClear = () => {
    setSelectedFile(null);
    setUrlInput("");
    setMarkdownOutput("");
    setError("");
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const handleConvert = async () => {
    if (!selectedFile && !urlInput.trim()) return;

    setIsConverting(true);
    setError("");

    const formData = new FormData();
    if (selectedFile) formData.append("file", selectedFile);
    if (urlInput.trim()) formData.append("url", urlInput.trim());

    try {
      // Pointing to the FastAPI backend running on port 8001
      const response = await fetch("http://localhost:8001/api/convert", {
        method: "POST",
        headers: {
          "X-API-Key": process.env.NEXT_PUBLIC_BAREMD_API_KEY || "default_secret_key_123"
        },
        body: formData,
      });

      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.detail || "Conversion failed");
      }

      const data = await response.json();
      setMarkdownOutput(data.markdown);
    } catch (err: any) {
      setError(err.message || "An unexpected error occurred during conversion.");
    } finally {
      setIsConverting(false);
    }
  };

  const handleDownload = () => {
    if (!markdownOutput) return;
    const blob = new Blob([markdownOutput], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = selectedFile ? `${selectedFile.name}.md` : "converted.md";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
  };

  return (
    <div className="min-h-screen bg-neutral-50 dark:bg-neutral-950 text-neutral-900 dark:text-neutral-100 flex flex-col font-sans">
      <NavbarFloating 
        logo={
          <div className="flex items-center gap-2 font-bold text-lg tracking-tight">
            BareMD
          </div>
        }
        links={[]} 
        actions={<div className="text-sm text-muted-foreground mr-4">v0.1.6</div>} 
        className="sticky top-0 z-50 pt-6"
      />

      <main className="flex-1 w-full max-w-7xl mx-auto p-4 md:p-8 flex flex-col md:flex-row gap-6 lg:gap-12 mt-4">
        
        {/* Left Column: Input / Upload Zone */}
        <div className="w-full md:w-1/2 flex flex-col gap-6">
          <div>
            <h1 className="text-3xl font-bold tracking-tight mb-2">Convert Documents</h1>
            <p className="text-muted-foreground">Upload any document, PDF, Excel, or HTML file and instantly convert it to clean Markdown.</p>
          </div>

          {/* Upload Area */}
          <div 
            className={`relative flex flex-col items-center justify-center p-12 border-2 border-dashed rounded-2xl transition-all duration-300 ease-in-out bg-white/50 dark:bg-neutral-900/50 backdrop-blur-sm
              ${isDragging ? 'border-primary bg-primary/5 dark:bg-primary/10 scale-[1.02]' : 'border-neutral-200 dark:border-neutral-800 hover:border-neutral-300 dark:hover:border-neutral-700 hover:bg-white dark:hover:bg-neutral-900'}
            `}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
          >
            <input 
              type="file" 
              ref={fileInputRef} 
              className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10" 
              onChange={handleFileChange}
              title="Drag and drop or click to upload"
            />
            
            <div className="flex flex-col items-center text-center gap-4 pointer-events-none">
              <div className="p-4 bg-primary/10 rounded-full text-primary">
                <UploadCloud size={32} />
              </div>
              <div>
                <p className="text-lg font-medium">Drag & Drop or click to upload</p>
                <p className="text-sm text-muted-foreground mt-1">Supports PDF, DOCX, PPTX, XLSX, HTML, Audio, etc.</p>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-4 py-1">
            <div className="flex-1 h-px bg-neutral-200 dark:bg-neutral-800"></div>
            <span className="text-xs font-medium text-neutral-400 uppercase tracking-widest">OR</span>
            <div className="flex-1 h-px bg-neutral-200 dark:bg-neutral-800"></div>
          </div>

          {/* URL Input */}
          <div className="relative group">
            <input
              type="text"
              value={urlInput}
              onChange={(e) => {
                setUrlInput(e.target.value);
                if (e.target.value) setSelectedFile(null);
              }}
              placeholder="Paste a YouTube, Wikipedia, or web URL..."
              className="w-full bg-white dark:bg-neutral-900/50 border border-neutral-200 dark:border-neutral-800 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all placeholder:text-neutral-400 dark:placeholder:text-neutral-600"
            />
          </div>

          {/* Selected File Details */}
          {selectedFile && (
            <div className="flex items-center justify-between p-4 bg-white dark:bg-neutral-900 rounded-xl shadow-sm border border-neutral-100 dark:border-neutral-800 animate-in fade-in slide-in-from-bottom-4">
              <div className="flex items-center gap-3 overflow-hidden">
                <div className="p-2 bg-blue-50 dark:bg-blue-900/20 text-blue-500 rounded-lg">
                  <FileIcon size={20} />
                </div>
                <div className="flex flex-col overflow-hidden">
                  <span className="text-sm font-medium truncate">{selectedFile.name}</span>
                  <span className="text-xs text-muted-foreground">{formatFileSize(selectedFile.size)}</span>
                </div>
              </div>
              <button 
                onClick={handleClear}
                className="p-2 text-neutral-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors"
                title="Remove file"
              >
                <X size={18} />
              </button>
            </div>
          )}

          {urlInput && (
            <div className="flex items-center justify-between p-4 bg-white dark:bg-neutral-900 rounded-xl shadow-sm border border-neutral-100 dark:border-neutral-800 animate-in fade-in slide-in-from-bottom-4">
              <div className="flex items-center gap-3 overflow-hidden">
                <div className="p-2 bg-purple-50 dark:bg-purple-900/20 text-purple-500 rounded-lg">
                  <FileIcon size={20} />
                </div>
                <div className="flex flex-col overflow-hidden">
                  <span className="text-sm font-medium truncate">{urlInput}</span>
                  <span className="text-xs text-muted-foreground">Web URL</span>
                </div>
              </div>
              <button 
                onClick={handleClear}
                className="p-2 text-neutral-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors"
                title="Remove URL"
              >
                <X size={18} />
              </button>
            </div>
          )}

          {error && (
            <div className="p-4 bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 rounded-xl text-sm border border-red-100 dark:border-red-900/30">
              {error}
            </div>
          )}

          {/* Action Button */}
          <button
            onClick={handleConvert}
            disabled={(!selectedFile && !urlInput.trim()) || isConverting}
            className={`mt-auto relative w-full py-4 px-6 rounded-xl font-medium text-white shadow-lg transition-all duration-300
              ${(!selectedFile && !urlInput.trim()) 
                ? 'bg-neutral-300 dark:bg-neutral-800 text-neutral-500 dark:text-neutral-500 shadow-none cursor-not-allowed' 
                : 'bg-neutral-900 hover:bg-neutral-800 dark:bg-neutral-100 dark:text-neutral-900 dark:hover:bg-white hover:shadow-xl hover:-translate-y-0.5'}
            `}
          >
            {isConverting ? (
              <span className="flex items-center justify-center gap-2">
                <Loader2 className="animate-spin" size={20} />
                Converting...
              </span>
            ) : (
              "Convert to Markdown"
            )}
          </button>
        </div>

        {/* Right Column: Output / Preview */}
        <div className="w-full md:w-1/2 flex flex-col bg-white dark:bg-neutral-900 rounded-3xl shadow-sm border border-neutral-200/50 dark:border-neutral-800/50 overflow-hidden relative">
          
          {/* Header Action Bar */}
          <div className="flex items-center justify-between px-6 py-4 border-b border-neutral-100 dark:border-neutral-800 bg-neutral-50/50 dark:bg-neutral-950/50">
            <h2 className="font-semibold text-sm tracking-wide uppercase text-neutral-500 dark:text-neutral-400">Output Preview</h2>
            
            <div className="flex items-center gap-2">
              <ButtonCopy 
                value={markdownOutput} 
                label="Copy" 
                showLabel={true} 
                sound={true} 
                style={{ opacity: markdownOutput ? 1 : 0.5, pointerEvents: markdownOutput ? 'auto' : 'none' }}
              />
              <button
                onClick={handleDownload}
                disabled={!markdownOutput}
                className={`flex items-center justify-center p-2 rounded-lg transition-colors border
                  ${!markdownOutput 
                    ? 'border-transparent text-neutral-400 cursor-not-allowed' 
                    : 'border-neutral-200 dark:border-neutral-700 bg-white dark:bg-neutral-800 text-neutral-700 dark:text-neutral-200 hover:bg-neutral-50 dark:hover:bg-neutral-700'}
                `}
                title="Download .md file"
              >
                <Download size={18} />
              </button>
            </div>
          </div>

          {/* Text Area */}
          <div className="flex-1 relative bg-[#FAFAFA] dark:bg-[#111111]">
            {markdownOutput ? (
              <textarea
                readOnly
                value={markdownOutput}
                className="absolute inset-0 w-full h-full p-6 bg-transparent resize-none focus:outline-none text-sm font-mono text-neutral-800 dark:text-neutral-300 leading-relaxed custom-scrollbar"
                placeholder="Markdown output will appear here..."
              />
            ) : (
              <div className="absolute inset-0 flex flex-col items-center justify-center text-center p-8">
                <div className="w-20 h-20 mb-6 rounded-full bg-neutral-100 dark:bg-neutral-800 flex items-center justify-center border border-neutral-200 dark:border-neutral-700">
                  <span className="text-3xl text-neutral-300 dark:text-neutral-600 font-mono">M↓</span>
                </div>
                <p className="text-neutral-400 dark:text-neutral-500 max-w-[250px]">
                  Upload a document and click convert to see the markdown output here.
                </p>
              </div>
            )}
          </div>
        </div>
      </main>
      
      {/* Custom scrollbar styles for the textarea */}
      <style dangerouslySetInnerHTML={{__html: `
        .custom-scrollbar::-webkit-scrollbar {
          width: 8px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: transparent;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background-color: rgba(156, 163, 175, 0.3);
          border-radius: 20px;
        }
        .dark .custom-scrollbar::-webkit-scrollbar-thumb {
          background-color: rgba(75, 85, 99, 0.4);
        }
      `}} />
    </div>
  );
}
