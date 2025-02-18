export interface File {
  id: string;
  original_filename: string;
  file_type: string;
  size: number;
  created_at: string;
  updated_at: string;
  file: string;
  content_hash: string;
  is_original: boolean;
  original_file?: string;
  sequence_number: number;
  similarity_score?: number;
  display_name: string;
  storage_path: string;
  similarity_info?: {
    score: number;
    original_file: {
      id: string;
      filename: string;
      created_at: string;
    };
  };
}

export interface StorageQuota {
  used: number;
  total: number;
  percentage: number;
} 