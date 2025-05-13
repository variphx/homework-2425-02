"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Slider } from "@/components/ui/slider";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

interface PerformanceSettingsProps {
  onChangeResolution: (width: number, height: number) => void;
  onChangeQuality: (quality: number) => void;
  onChangeInterval: (interval: number) => void;
  defaultQuality?: number;
  defaultInterval?: number;
}

export default function PerformanceSettings({
  onChangeResolution,
  onChangeQuality,
  onChangeInterval,
  defaultQuality = 0.9,
  defaultInterval = 1,
}: PerformanceSettingsProps) {
  const [quality, setQuality] = useState(defaultQuality);
  const [interval, setInterval] = useState(defaultInterval);

  const handleQualityChange = (value: number[]) => {
    const newQuality = value[0];
    setQuality(newQuality);
    onChangeQuality(newQuality);
  };

  const handleIntervalChange = (value: number[]) => {
    const newInterval = value[0];
    setInterval(newInterval);
    onChangeInterval(newInterval);
  };

  const handleResolutionChange = (value: string) => {
    const [width, height] = value.split("x").map(Number);
    onChangeResolution(width, height);
  };

  return (
    <Card className="w-full">
      <CardHeader className="pb-2">
        <CardTitle className="text-sm">Cài đặt hiệu suất</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-2">
          <Label htmlFor="resolution">Độ phân giải</Label>
          <Select onValueChange={handleResolutionChange} defaultValue="640x480">
            <SelectTrigger id="resolution">
              <SelectValue placeholder="Chọn độ phân giải" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="320x240">320x240 (Thấp)</SelectItem>
              <SelectItem value="640x480">640x480 (Trung bình)</SelectItem>
              <SelectItem value="1280x720">1280x720 (HD)</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-2">
          <div className="flex justify-between">
            <Label htmlFor="quality">
              Chất lượng ảnh: {Math.round(quality * 100)}%
            </Label>
          </div>
          <Slider
            id="quality"
            min={0.1}
            max={1}
            step={0.05}
            value={[quality]}
            onValueChange={handleQualityChange}
          />
          <div className="text-xs text-gray-500">
            Chất lượng thấp hơn = tốc độ nhanh hơn, nhưng độ chính xác thấp hơn
          </div>
        </div>

        <div className="space-y-2">
          <div className="flex justify-between">
            <Label htmlFor="interval">Chu kỳ phát hiện: {interval}ms</Label>
          </div>
          <Slider
            id="interval"
            min={200}
            max={2000}
            step={100}
            value={[interval]}
            onValueChange={handleIntervalChange}
          />
          <div className="text-xs text-gray-500">
            Chu kỳ ngắn hơn = cập nhật nhanh hơn, nhưng tải CPU cao hơn
          </div>
        </div>

        <div className="grid grid-cols-2 gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => {
              setQuality(0.5);
              setInterval(1000);
              onChangeQuality(0.5);
              onChangeInterval(1000);
              onChangeResolution(640, 480);
            }}
          >
            Cân bằng
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => {
              setQuality(0.3);
              setInterval(500);
              onChangeQuality(0.3);
              onChangeInterval(500);
              onChangeResolution(320, 240);
            }}
          >
            Tốc độ cao
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
