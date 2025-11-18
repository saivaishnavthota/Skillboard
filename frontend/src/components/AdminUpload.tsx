/** Admin upload component for Excel files. */
import React, { useState, useRef } from 'react';
import { adminApi, UploadResponse } from '../services/api';

interface AdminUploadProps {
  uploadType: 'skills' | 'employee-skills';
}

export const AdminUpload: React.FC<AdminUploadProps> = ({ uploadType }) => {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<any[]>([]);
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState<UploadResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (!selectedFile) return;

    setFile(selectedFile);
    setError(null);
    setResult(null);

    // Preview first 10 rows
    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      
      // For preview, we'll read the file client-side if possible
      // For now, just show file name
      setPreview([]);
    } catch (err) {
      console.error('Error reading file:', err);
    }
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile && fileInputRef.current) {
      // Create a new FileList-like object
      const dataTransfer = new DataTransfer();
      dataTransfer.items.add(droppedFile);
      fileInputRef.current.files = dataTransfer.files;
      handleFileSelect({ target: { files: dataTransfer.files } } as any);
    }
  };

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
  };

  const handleUpload = async () => {
    if (!file) return;

    setUploading(true);
    setError(null);
    setResult(null);

    try {
      const response =
        uploadType === 'skills'
          ? await adminApi.uploadSkills(file)
          : await adminApi.uploadEmployeeSkills(file);
      setResult(response);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Upload failed');
    } finally {
      setUploading(false);
    }
  };

  const title =
    uploadType === 'skills'
      ? 'Upload Master Skills'
      : 'Upload Employee Skills';
  const description =
    uploadType === 'skills'
      ? 'Upload Excel/CSV with columns: name, description (optional)'
      : 'Upload Excel/CSV with columns: EmployeeID, EmployeeName, SkillName, Rating, YearsExperience (optional)';

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h3 className="text-lg font-semibold mb-4">{title}</h3>
      <p className="text-sm text-gray-600 mb-4">{description}</p>

      {/* Drag and drop area */}
      <div
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        className={`
          border-2 border-dashed rounded-lg p-8 text-center
          ${file ? 'border-green-400 bg-green-50' : 'border-gray-300 bg-gray-50'}
          hover:border-blue-400 transition-colors cursor-pointer
        `}
        onClick={() => fileInputRef.current?.click()}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".xlsx,.xls,.csv"
          onChange={handleFileSelect}
          className="hidden"
        />
        {file ? (
          <div>
            <p className="text-green-700 font-medium">{file.name}</p>
            <p className="text-sm text-gray-500 mt-2">
              {(file.size / 1024).toFixed(2)} KB
            </p>
          </div>
        ) : (
          <div>
            <p className="text-gray-600">Drag & drop file here</p>
            <p className="text-sm text-gray-500 mt-2">or click to browse</p>
          </div>
        )}
      </div>

      {/* Upload button */}
      {file && (
        <button
          onClick={handleUpload}
          disabled={uploading}
          className={`
            mt-4 w-full py-2 px-4 rounded-lg font-medium
            ${uploading
              ? 'bg-gray-400 cursor-not-allowed'
              : 'bg-blue-600 hover:bg-blue-700 text-white'
            }
            transition-colors
          `}
        >
          {uploading ? 'Uploading...' : 'Upload'}
        </button>
      )}

      {/* Error message */}
      {error && (
        <div className="mt-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
          {error}
        </div>
      )}

      {/* Success message */}
      {result && (
        <div className="mt-4 p-3 bg-green-100 border border-green-400 text-green-700 rounded">
          <p className="font-medium">{result.message}</p>
          <p className="text-sm mt-1">
            Processed: {result.rows_processed} | Created: {result.rows_created} |
            Updated: {result.rows_updated}
          </p>
          {result.errors && result.errors.length > 0 && (
            <div className="mt-2">
              <p className="font-medium">Errors:</p>
              <ul className="list-disc list-inside text-sm">
                {result.errors.slice(0, 10).map((err, idx) => (
                  <li key={idx}>{err}</li>
                ))}
                {result.errors.length > 10 && (
                  <li>... and {result.errors.length - 10} more</li>
                )}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

