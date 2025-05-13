"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Loader2,
  Camera,
  CameraOff,
  UserPlus,
  UserCheck,
  Bug,
} from "lucide-react";
import WebcamDetection from "@/components/web-cam-detection";
import DebugPanel from "@/components/debug-panel";

export default function Home() {
  const [isWebcamActive, setIsWebcamActive] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isRecognitionEnabled, setIsRecognitionEnabled] = useState(true);
  const [registerMode, setRegisterMode] = useState(false);
  const [name, setName] = useState("");
  const [detections, setDetections] = useState<any[]>([]);
  const [registrationStatus, setRegistrationStatus] = useState<string | null>(
    null
  );
  const [showDebugPanel, setShowDebugPanel] = useState(false);
  const [detectionInterval, setDetectionInterval] = useState(50); // Mặc định 50ms

  const toggleWebcam = () => {
    if (isWebcamActive) {
      setIsWebcamActive(false);
      setDetections([]);
    } else {
      setIsLoading(true);
      setIsWebcamActive(true);
    }
  };

  const handleRegister = async (imageBlob: Blob) => {
    if (!name) {
      setRegistrationStatus("Vui lòng nhập tên trước khi đăng ký");
      return false;
    }

    const formData = new FormData();
    formData.append("image", imageBlob);
    formData.append("name", name);

    try {
      setRegistrationStatus("Đang đăng ký...");
      const response = await fetch("/api/register", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response
          .json()
          .catch(() => ({ error: "Unknown error" }));
        throw new Error(
          errorData.error || `Registration failed: ${response.status}`
        );
      }

      const data = await response.json();

      if (data.status === "ok") {
        setRegistrationStatus("Đăng ký thành công!");
        return true;
      } else {
        setRegistrationStatus(
          "Đăng ký thất bại: " + (data.error || "Lỗi không xác định")
        );
        return false;
      }
    } catch (error) {
      console.error("Registration error:", error);
      setRegistrationStatus(
        `Đăng ký thất bại: ${error instanceof Error ? error.message : "Lỗi kết nối"
        }`
      );
      return false;
    }
  };

  const handleDetections = (newDetections: any[]) => {
    setDetections(newDetections);
  };

  // Hàm xử lý thay đổi chu kỳ phát hiện
  const handleIntervalChange = (value: number[]) => {
    setDetectionInterval(value[0]);
  };

  return (
    <main className="flex min-h-screen flex-col items-center p-4 md:p-8 bg-gray-50">
      <h1 className="text-3xl font-bold mb-8 text-center">
        Hệ thống nhận diện khuôn mặt
      </h1>

      <Card className="w-full max-w-3xl">
        <CardHeader>
          <CardTitle className="flex justify-between items-center">
            <span>Camera</span>
            <div className="flex gap-2">

              <Button
                onClick={toggleWebcam}
                variant="outline"
                className="flex items-center gap-2"
              >
                {isWebcamActive ? (
                  <>
                    <CameraOff className="h-4 w-4" /> Tắt Camera
                  </>
                ) : (
                  <>
                    <Camera className="h-4 w-4" /> Bật Camera
                  </>
                )}
              </Button>
            </div>
          </CardTitle>
        </CardHeader>
        <CardContent>
          {registerMode && (
            <div className="mb-4">
              <Label htmlFor="name">Tên người dùng</Label>
              <input
                id="name"
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="w-full p-2 border rounded mt-1"
                placeholder="Nhập tên người dùng"
              />
            </div>
          )}

          <div className="relative aspect-video bg-gray-100 rounded-md overflow-hidden flex items-center justify-center border">
            {isLoading && isWebcamActive && (
              <div className="absolute inset-0 flex items-center justify-center bg-black/10 z-10">
                <Loader2 className="h-8 w-8 animate-spin text-primary" />
              </div>
            )}

            {!isWebcamActive && (
              <div className="text-gray-500 flex flex-col items-center gap-2">
                <Camera className="h-12 w-12" />
                <p>Bấm "Bật Camera" để bắt đầu</p>
              </div>
            )}

            {isWebcamActive && (
              <WebcamDetection
                onLoadComplete={() => setIsLoading(false)}
                onDetections={handleDetections}
                onRegister={handleRegister}
                registerMode={registerMode}
                detectionInterval={detectionInterval}
              />
            )}
          </div>

          {/* Hiển thị chu kỳ phát hiện cố định */}
          {isWebcamActive && !registerMode && (
            <div className="mt-4 p-2 bg-blue-50 border border-blue-200 rounded-md">
              <p className="text-sm font-medium">Chu kỳ phát hiện: 1ms</p>
              <p className="text-xs text-gray-500">
                Chu kỳ ngắn giúp cập nhật nhanh hơn, nhưng có thể tăng tải CPU
              </p>
            </div>
          )}


          {detections.length > 0 && !registerMode && (
            <div className="mt-4 space-y-2">
              <p className="font-medium">Kết quả nhận diện:</p>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
              </div>
            </div>
          )}

          {registerMode && (
            <div className="mt-4 p-3 bg-green-50 rounded-md border border-green-200">
              <p className="font-medium">Chế độ đăng ký khuôn mặt</p>
              <p>Nhập tên và đưa mặt vào khung hình để đăng ký</p>
            </div>
          )}

          {registerMode && registrationStatus && (
            <div
              className={`mt-2 p-2 rounded-md border text-sm ${registrationStatus.includes("thành công")
                ? "bg-green-50 border-green-200"
                : "bg-red-50 border-red-200"
                }`}
            >
              {registrationStatus}
            </div>
          )}
        </CardContent>
      </Card>

      <div className="mt-8 text-center text-sm text-gray-500 max-w-xl">
      </div>
      {/* Thêm nút debug ở góc dưới bên trái */}
      <Button
        variant="outline"
        size="sm"
        className="fixed bottom-4 left-4 bg-white/80 backdrop-blur-sm"
        onClick={() => setShowDebugPanel(!showDebugPanel)}
      >
        <Bug className="h-4 w-4 mr-2" />
        Debug
      </Button>

      <DebugPanel
        isVisible={showDebugPanel}
        onClose={() => setShowDebugPanel(false)}
      />
    </main>
  );
}
