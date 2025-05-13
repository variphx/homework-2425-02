import { type NextRequest, NextResponse } from "next/server";

export async function POST(request: NextRequest) {
  const startTime = performance.now();

  try {
    const formData = await request.formData();
    const image = formData.get("image") as File;

    if (!image) {
      return NextResponse.json({ error: "Missing image" }, { status: 400 });
    }

    // Log kích thước ảnh để debug
    console.log(`Image size: ${(image.size / 1024).toFixed(2)} KB`);

    // Get the Hugging Face Space URL from environment variables
    const hfSpaceUrl = process.env.NEXT_PUBLIC_HF_SPACE_URL;

    if (!hfSpaceUrl) {
      console.error("NEXT_PUBLIC_HF_SPACE_URL is not configured");
      return NextResponse.json(
        { error: "API URL not configured" },
        { status: 500 }
      );
    }

    // Create a new FormData object to send to the Hugging Face Space
    const apiFormData = new FormData();
    apiFormData.append("file", image);

    console.log(`Sending request to http://localhost:8000/api/v1/predictions`);

    const apiStartTime = performance.now();
    // Call the Hugging Face Space API
    const response = await fetch(`http://localhost:8000/api/v1/predictions`, {
      method: "POST",
      body: apiFormData,
    });
    const apiEndTime = performance.now();

    if (!response.ok) {
      const errorText = await response.text();
      console.error(`Hugging Face API error (${response.status}):`, errorText);
      return NextResponse.json(
        { error: `API error: ${response.status}` },
        { status: response.status }
      );
    }

    const detections = await response.json();
    detections.score = 0.5;
    const endTime = performance.now();

    console.log("Recognition results:", detections);
    console.log(
      `API response time: ${Math.round(
        apiEndTime - apiStartTime
      )}ms, Total processing time: ${Math.round(endTime - startTime)}ms`
    );

    // Đảm bảo định dạng dữ liệu trả về đúng với định dạng từ Python backend
    // Python backend trả về: {"bbox": [x1, y1, x2, y2], "label": "name", "score": 0.95}
    return NextResponse.json(detections);
  } catch (error) {
    console.error("Recognition error:", error);
    return NextResponse.json(
      { error: "Failed to process recognition request" },
      { status: 500 }
    );
  }
}
