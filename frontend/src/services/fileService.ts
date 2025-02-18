import axios from 'axios';
import { File as FileType, StorageQuota } from '../types/file';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

// Configure axios defaults
axios.defaults.withCredentials = true;  // Important for session cookie handling

export const fileService = {
  async uploadFile(file: File): Promise<{
    file: FileType;
    is_duplicate?: boolean;
    similar_file?: FileType;
    similarity?: number;
  }> {
    console.log('Starting file upload:', file.name);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post(`${API_URL}/files/`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        withCredentials: true,
      });
      console.log('Upload API response:', response.data);
      return response.data;
    } catch (error) {
      console.error('Upload API error:', error);
      throw error;
    }
  },

  async getFiles(): Promise<FileType[]> {
    const response = await axios.get(`${API_URL}/files/`, {
      withCredentials: true,
    });
    return response.data;
  },

  async deleteFile(id: string): Promise<void> {
    await axios.delete(`${API_URL}/files/${id}/`, {
      withCredentials: true,
    });
  },

  async downloadFile(fileUrl: string, filename: string): Promise<void> {
    try {
      const response = await axios.get(fileUrl, {
        responseType: 'blob',
        withCredentials: true,
      });
      
      // Create a blob URL and trigger download
      const blob = new Blob([response.data]);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Download error:', error);
      throw new Error('Failed to download file');
    }
  },

  async getStorageQuota(): Promise<StorageQuota> {
    const response = await axios.get(`${API_URL}/files/storage_usage/`, {
      withCredentials: true,
    });
    return response.data;
  },
}; 