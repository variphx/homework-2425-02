"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Bug, RefreshCw, X } from "lucide-react";

interface DebugPanelProps {
  isVisible?: boolean;
  onClose?: () => void;
}

export default function DebugPanel({
  isVisible = false,
  onClose,
}: DebugPanelProps) {
  const [isOpen, setIsOpen] = useState(isVisible);
  const [apiStatus, setApiStatus] = useState<{
    ok: boolean;
    message: string;
  } | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    setIsOpen(isVisible);
  }, [isVisible]);

  const checkApiStatus = async () => {
    setIsLoading(true);
    try {
      const response = await fetch("/api/status");
      const data = await response.json();
      setApiStatus(data);
    } catch (error) {
      setApiStatus({
        ok: false,
        message:
          error instanceof Error ? error.message : "Không thể kết nối đến API",
      });
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      checkApiStatus();
    }
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <Card className="fixed bottom-4 right-4 w-80 shadow-lg z-50">
      <CardHeader className="pb-2">
        <CardTitle className="text-sm flex justify-between items-center">
          <div className="flex items-center gap-2">
            <Bug className="h-4 w-4" />
            Thông tin Debug
          </div>
          <Button
            variant="ghost"
            size="sm"
            className="h-6 w-6 p-0"
            onClick={() => {
              setIsOpen(false);
              onClose?.();
            }}
          >
            <X className="h-4 w-4" />
          </Button>
        </CardTitle>
      </CardHeader>
      <CardContent className="text-xs space-y-2">
        <div className="space-y-1">
          <div className="font-medium">Trạng thái API:</div>
          <div className="flex items-center gap-2">
            {apiStatus ? (
              <div
                className={`px-2 py-1 rounded ${
                  apiStatus.ok
                    ? "bg-green-100 text-green-800"
                    : "bg-red-100 text-red-800"
                }`}
              >
                {apiStatus.message}
              </div>
            ) : (
              <div className="text-gray-500">Chưa kiểm tra</div>
            )}
            <Button
              variant="outline"
              size="sm"
              className="h-6 px-2 ml-auto"
              onClick={checkApiStatus}
              disabled={isLoading}
            >
              {isLoading ? (
                <RefreshCw className="h-3 w-3 animate-spin" />
              ) : (
                "Kiểm tra"
              )}
            </Button>
          </div>
        </div>

        <div className="space-y-1">
          <div className="font-medium">Biến môi trường:</div>
          <div className="bg-gray-100 p-2 rounded text-xs font-mono overflow-x-auto">
            <div>
              NEXT_PUBLIC_HF_SPACE_URL:{" "}
              {process.env.NEXT_PUBLIC_HF_SPACE_URL || "Chưa cấu hình"}
            </div>
            <div>
              HF_API_TOKEN:{" "}
              {process.env.HF_API_TOKEN ? "✓ Đã cấu hình" : "✗ Chưa cấu hình"}
            </div>
            <div>
              HF_MODEL_NAME:{" "}
              {process.env.HF_MODEL_NAME || "Chưa cấu hình (sử dụng mặc định)"}
            </div>
          </div>
        </div>

        <div className="space-y-1">
          <div className="font-medium">Thông tin trình duyệt:</div>
          <div className="bg-gray-100 p-2 rounded text-xs font-mono overflow-x-auto">
            <div>User Agent: {navigator.userAgent}</div>
            <div>
              Kích thước màn hình: {window.innerWidth}x{window.innerHeight}
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
