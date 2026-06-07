import React, { useState, useEffect } from 'react';
import { uploadDocument, listDocuments, deleteDocument, DocumentResponse } from '../services/api';

export const DocumentManager: React.FC = () => {
  const [documents, setDocuments] = useState<DocumentResponse[]>([]);
  const [isDragging, setIsDragging] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // 加载文档列表
  useEffect(() => {
    loadDocuments();
  }, []);

  const loadDocuments = async () => {
    try {
      setIsLoading(true);
      const docs = await listDocuments();
      setDocuments(docs);
    } catch (err) {
      setError(err instanceof Error ? err.message : '加载文档失败');
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileUpload = async (files: FileList | null) => {
    if (!files || files.length === 0) return;

    try {
      setIsLoading(true);
      setError(null);

      for (const file of Array.from(files)) {
        await uploadDocument(file);
      }

      // 重新加载列表
      await loadDocuments();
    } catch (err) {
      setError(err instanceof Error ? err.message : '上传失败');
    } finally {
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

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    handleFileUpload(e.dataTransfer.files);
  };

  const handleDeleteDocument = async (documentId: string) => {
    try {
      setIsLoading(true);
      await deleteDocument(documentId);
      // 重新加载列表
      await loadDocuments();
    } catch (err) {
      setError(err instanceof Error ? err.message : '删除失败');
    } finally {
      setIsLoading(false);
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-2xl font-bold text-gray-800 mb-6">文档管理</h2>

      {/* 错误提示 */}
      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-600 rounded-md text-sm">
          {error}
        </div>
      )}

      {/* 文件上传区域 */}
      <div
        data-testid="drop-zone"
        className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
          isDragging
            ? 'border-blue-500 bg-blue-50'
            : 'border-gray-300 hover:border-gray-400'
        }`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <div className="mx-auto max-w-md">
          <svg
            className="mx-auto h-12 w-12 text-gray-400"
            stroke="currentColor"
            fill="none"
            viewBox="0 0 48 48"
            aria-hidden="true"
          >
            <path
              d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
              strokeWidth={2}
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
          <div className="mt-4">
            <p className="text-lg text-gray-600">
              拖拽文件到此处上传，或
              <label className="text-blue-500 hover:text-blue-600 cursor-pointer ml-1">
                点击选择文件
                <input
                  type="file"
                  className="hidden"
                  multiple
                  onChange={(e) => handleFileUpload(e.target.files)}
                />
              </label>
            </p>
            <p className="text-sm text-gray-500 mt-2">
              支持 PDF、DOC、TXT 等格式
            </p>
          </div>
        </div>
      </div>

      {/* 文档列表 */}
      <div data-testid="document-list" className="mt-6">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold text-gray-800">
            已上传文档 ({documents.length})
          </h3>
          <button
            onClick={loadDocuments}
            disabled={isLoading}
            className="text-sm text-blue-500 hover:text-blue-600 disabled:opacity-50"
          >
            刷新
          </button>
        </div>

        {isLoading ? (
          <div className="text-center py-8 text-gray-500">加载中...</div>
        ) : documents.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            暂无文档，请上传文件
          </div>
        ) : (
          <div className="space-y-3">
            {documents.map((doc) => (
              <div
                key={doc.document_id}
                className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
              >
                <div className="flex items-center space-x-3">
                  <div className="flex-shrink-0">
                    <svg
                      className="h-8 w-8 text-gray-400"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                      />
                    </svg>
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 truncate">
                      {doc.filename}
                    </p>
                    <p className="text-xs text-gray-500">
                      {doc.uploaded_at}
                    </p>
                  </div>
                </div>
                <button
                  onClick={() => handleDeleteDocument(doc.document_id)}
                  disabled={isLoading}
                  className="flex-shrink-0 ml-4 px-3 py-1 text-sm text-red-600 hover:text-red-800 hover:bg-red-50 rounded transition-colors disabled:opacity-50"
                >
                  删除
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
