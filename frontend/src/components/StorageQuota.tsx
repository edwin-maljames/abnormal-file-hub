import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { fileService } from '../services/fileService';

export const StorageQuota: React.FC = () => {
  const { data: quota, isLoading } = useQuery({
    queryKey: ['storage-quota'],
    queryFn: fileService.getStorageQuota,
  });

  if (isLoading || !quota) {
    return (
      <div className="animate-pulse h-2 bg-gray-200 rounded"></div>
    );
  }

  const getColorClass = (percentage: number) => {
    if (percentage >= 90) return 'bg-red-500';
    if (percentage >= 70) return 'bg-yellow-500';
    return 'bg-primary-500';
  };

  return (
    <div className="mb-4">
      <div className="flex justify-between text-sm text-gray-600 mb-1">
        <span>Storage Used</span>
        <span>
          {(quota.used / (1024 * 1024)).toFixed(2)} MB / {(quota.total / (1024 * 1024)).toFixed(0)} MB
        </span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-2">
        <div
          className={`${getColorClass(quota.percentage)} h-2 rounded-full transition-all duration-300`}
          style={{ width: `${Math.min(quota.percentage, 100)}%` }}
        ></div>
      </div>
      {quota.percentage >= 90 && (
        <p className="text-xs text-red-600 mt-1">
          Storage almost full! Please delete some files.
        </p>
      )}
      {quota.percentage >= 70 && quota.percentage < 90 && (
        <p className="text-xs text-yellow-600 mt-1">
          Storage usage is high.
        </p>
      )}
    </div>
  );
}; 