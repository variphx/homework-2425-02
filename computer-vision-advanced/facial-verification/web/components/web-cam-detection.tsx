"use client";

import { useEffect, useRef, useState } from "react";

interface Detection {
  bbox: [number, number, number, number];
  label: string;
  score: number;
}

interface WebcamDetectionProps {
  onDetections?: (detections: Detection[]) => void;
  onRegister?: (imageBlob: Blob) => Promise<boolean>;
  registerMode?: boolean;
  onLoadComplete?: () => void;
  detectionInterval?: number;
  wsUrl?: string; // Optional WebSocket URL
}

export default function WebcamDetection({
  onDetections,
  onRegister,
  registerMode = false,
  onLoadComplete,
  detectionInterval = 100, // Slightly increased interval for WebSocket
  wsUrl = process.env.NEXT_PUBLIC_WEBSOCKET_URL ||
    "ws://localhost:8000/ws/predictions", // Configurable WebSocket URL
}: WebcamDetectionProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const websocketRef = useRef<WebSocket | null>(null);

  const [isStreamActive, setIsStreamActive] = useState(false);
  const detectionIntervalRef = useRef<NodeJS.Timeout>();
  const animationFrameRef = useRef<number>();
  const [lastDetections, setLastDetections] = useState<Detection[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const processingRef = useRef(false);
  const lastDetectionsRef = useRef<Detection[]>([]);
  const currentIntervalRef = useRef(detectionInterval);

  // WebSocket connection effect
  useEffect(() => {
    // Log WebSocket URL for debugging
    console.log("Connecting to WebSocket URL:", wsUrl);

    // Establish WebSocket connection
    const socket = new WebSocket(wsUrl);
    websocketRef.current = socket;

    socket.onopen = () => {
      console.log("WebSocket connection established successfully");
    };

    socket.onerror = (error) => {
      console.error("WebSocket connection error:", error);
      setError(`Lỗi kết nối WebSocket: ${error}`);
    };

    socket.onclose = (event) => {
      console.log("WebSocket connection closed:", event);
      setError(
        `Mất kết nối WebSocket. Mã: ${event.code}, Lý do: ${event.reason}`
      );
    };

    return () => {
      socket.close();
    };
  }, [wsUrl]);

  // Start webcam and setup detection interval
  useEffect(() => {
    const startWebcam = async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: { facingMode: "user" },
        });

        if (videoRef.current) {
          videoRef.current.srcObject = stream;
          videoRef.current.onloadedmetadata = () => {
            videoRef.current?.play();
            setIsStreamActive(true);
            onLoadComplete?.();

            // Setup canvas dimensions
            if (canvasRef.current && videoRef.current) {
              canvasRef.current.width = videoRef.current.videoWidth;
              canvasRef.current.height = videoRef.current.videoHeight;
            }

            // Bắt đầu vòng lặp render
            startRenderLoop();

            // Bắt đầu chu kỳ phát hiện
            startDetectionLoop();
          };
        }
      } catch (error) {
        console.error("Error accessing webcam:", error);
        setError(
          "Không thể truy cập camera. Vui lòng kiểm tra quyền truy cập."
        );
      }
    };

    startWebcam();

    return () => {
      // Dọn dẹp khi component unmount
      clearInterval(detectionIntervalRef.current);
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
      if (videoRef.current?.srcObject) {
        const stream = videoRef.current.srcObject as MediaStream;
        stream.getTracks().forEach((track) => track.stop());
      }
    };
  }, []);

  // Cập nhật chu kỳ phát hiện khi prop thay đổi
  useEffect(() => {
    currentIntervalRef.current = detectionInterval;
    if (isStreamActive) {
      startDetectionLoop();
    }
  }, [detectionInterval]);

  // Hàm bắt đầu vòng lặp render liên tục
  const startRenderLoop = () => {
    const renderFrame = () => {
      if (!videoRef.current || !canvasRef.current) return;

      const ctx = canvasRef.current.getContext("2d");
      if (ctx) {
        // Vẽ khung hình video hiện tại
        ctx.drawImage(
          videoRef.current,
          0,
          0,
          canvasRef.current.width,
          canvasRef.current.height
        );

        // Vẽ lại các detections từ lần phát hiện gần nhất
        if (lastDetectionsRef.current.length > 0) {
          drawDetections(ctx, lastDetectionsRef.current);
        }
      }

      // Tiếp tục vòng lặp render
      animationFrameRef.current = requestAnimationFrame(renderFrame);
    };

    // Bắt đầu vòng lặp render
    animationFrameRef.current = requestAnimationFrame(renderFrame);
  };

  // Hàm bắt đầu chu kỳ phát hiện
  const startDetectionLoop = () => {
    // Xóa interval cũ nếu có
    if (detectionIntervalRef.current) {
      clearInterval(detectionIntervalRef.current);
    }

    // Thiết lập interval mới với chu kỳ hiện tại
    detectionIntervalRef.current = setInterval(async () => {
      // Chỉ xử lý nếu không có quá trình xử lý nào đang diễn ra
      if (!processingRef.current) {
        await processFrame();
      }
    }, currentIntervalRef.current);
  };

  const processFrame = async () => {
    if (
      !videoRef.current ||
      !canvasRef.current ||
      processingRef.current ||
      !websocketRef.current
    )
      return;

    processingRef.current = true;
    setIsProcessing(true);
    setError(null);

    try {
      // Capture frame
      const imageBlob = await captureFrame();

      if (registerMode && onRegister) {
        await onRegister(imageBlob);
        processingRef.current = false;
        setIsProcessing(false);
        return;
      }

      // Send image blob directly via WebSocket
      if (websocketRef.current?.readyState === WebSocket.OPEN) {
        websocketRef.current.send(imageBlob);
      }

      // Handle WebSocket response
      const handleResponse = (event: MessageEvent) => {
        try {
          const data = JSON.parse(event.data);
          console.log("WebSocket response:", data);

          if (data.error) {
            throw new Error(data.error);
          }

          // Process received detections
          const detections: Detection[] = Array.isArray(data) ? data : [];
          
          // Cập nhật cả state và ref để đảm bảo animation frame luôn có dữ liệu mới nhất
          setLastDetections(detections);
          lastDetectionsRef.current = detections;
          onDetections?.(detections);

          // Remove listener after processing
          websocketRef.current?.removeEventListener("message", handleResponse);
        } catch (parseError) {
          console.error("Error parsing WebSocket message:", parseError);
          setError(
            `Lỗi xử lý: ${
              parseError instanceof Error
                ? parseError.message
                : "Không xác định"
            }`
          );
        } finally {
          processingRef.current = false;
          setIsProcessing(false);
        }
      };

      // Add message listener
      websocketRef.current.addEventListener("message", handleResponse);
    } catch (error) {
      console.error("Processing error:", error);
      setError(
        `Lỗi xử lý: ${
          error instanceof Error ? error.message : "Không xác định"
        }`
      );
      processingRef.current = false;
      setIsProcessing(false);
    }
  };

  const captureFrame = (): Promise<Blob> => {
    return new Promise((resolve, reject) => {
      if (!videoRef.current || !canvasRef.current) {
        return reject("Video or canvas not available");
      }

      const canvas = document.createElement("canvas");
      canvas.width = videoRef.current.videoWidth;
      canvas.height = videoRef.current.videoHeight;
      const ctx = canvas.getContext("2d");

      if (ctx) {
        ctx.drawImage(videoRef.current, 0, 0);
        canvas.toBlob(
          (blob) => {
            blob ? resolve(blob) : reject("Failed to capture frame");
          },
          "image/jpeg",
          0.95 // Higher quality for better detection
        );
      } else {
        reject("Could not get canvas context");
      }
    });
  };

  // Tách hàm vẽ bounding box để có thể sử dụng trong animation frame
  const drawDetections = (
  ctx: CanvasRenderingContext2D,
  detections: Detection[]
) => {
  detections.forEach((det) => {
    if (!det.bbox || !Array.isArray(det.bbox) || det.bbox.length !== 4) {
      console.error("Invalid bbox data:", det.bbox);
      return;
    }

    const [x1, y1, x2, y2] = det.bbox;
    const width = x2 - x1;
    const height = y2 - y1;

    // Determine label and color based on score
    const isLowConfidence = det.score < 0.3;
    const label = isLowConfidence ? "unknown" : det.label;
    const color = isLowConfidence ? "#FF0066" : "#00FF88"; // Red or Green

    // Draw bounding box
    ctx.strokeStyle = color;
    ctx.lineWidth = 3;
    ctx.strokeRect(x1, y1, width, height);

    // Draw background for label
    ctx.fillStyle = color;
    const text = label === "unknown" ? "Không xác định" : label;
    const textWidth = ctx.measureText(text).width;
    ctx.fillRect(x1, y1 > 25 ? y1 - 25 : y1, textWidth + 10, 25);

    // Draw label text
    ctx.fillStyle = "#FFFFFF";
    ctx.font = "bold 16px Arial";
    ctx.fillText(text, x1 + 5, y1 > 25 ? y1 - 7 : y1 + 17);
  });
};

  // Thêm nút chụp ảnh thủ công
  const handleManualCapture = async () => {
    if (processingRef.current) return;
    await processFrame();
  };

  return (
    <div className="relative w-full h-full">
      <video
        ref={videoRef}
        className="absolute inset-0 w-full h-full object-cover"
        playsInline
        muted
      />
      <canvas
        ref={canvasRef}
        className="absolute inset-0 w-full h-full object-cover"
      />

      {isProcessing && (
        <div className="absolute top-2 right-2 bg-blue-500 text-white text-xs px-2 py-1 rounded-full animate-pulse">
          Đang xử lý...
        </div>
      )}

      {error && (
        <div className="absolute top-2 left-2 right-2 bg-red-500 text-white text-xs px-2 py-1 rounded text-center">
          {error}
        </div>
      )}

      {isStreamActive && (
        <div className="absolute bottom-2 left-2 bg-black/70 text-white text-xs px-2 py-1 rounded">
          {registerMode
            ? "Chế độ đăng ký"
            : `Đã phát hiện: ${lastDetections.length} khuôn mặt`}
        </div>
      )}

    </div>
  );
}