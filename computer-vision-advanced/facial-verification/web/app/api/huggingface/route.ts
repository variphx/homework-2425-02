import { type NextRequest, NextResponse } from "next/server";

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData();
    const image = formData.get("image") as File;

    if (!image) {
      return NextResponse.json({ error: "Missing image" }, { status: 400 });
    }

    // Get API token from environment variables - now server-side only
    const apiToken = process.env.HF_API_TOKEN;

    if (!apiToken) {
      console.error("HF_API_TOKEN is not configured");
      return NextResponse.json(
        { error: "API token not configured" },
        { status: 500 }
      );
    }

    // Get model name from environment variables or use default
    const modelName = process.env.HF_MODEL_NAME || "facebook/detr-resnet-50";

    // Get the Hugging Face API URL
    const HF_API_URL = "https://api-inference.huggingface.co/models";

    // Convert image to buffer
    const bytes = await image.arrayBuffer();
    const buffer = Buffer.from(bytes);

    console.log(
      `Sending request to Hugging Face API: ${HF_API_URL}/${modelName}`
    );

    // Call Hugging Face API
    const response = await fetch(`${HF_API_URL}/${modelName}`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${apiToken}`,
        "Content-Type": "application/octet-stream",
      },
      body: buffer,
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error(`Hugging Face API error (${response.status}):`, errorText);

      // If the model is loading, return a specific error
      if (errorText.includes("loading")) {
        return NextResponse.json(
          { error: "Model is loading, please try again in a moment" },
          { status: 503 }
        );
      }

      return NextResponse.json(
        { error: `API error: ${response.status}` },
        { status: response.status }
      );
    }

    const result = await response.json();
    console.log(
      "Hugging Face API response:",
      JSON.stringify(result).substring(0, 200) + "..."
    );

    return NextResponse.json(result);
  } catch (error) {
    console.error("Hugging Face processing error:", error);
    return NextResponse.json(
      { error: "Failed to process request" },
      { status: 500 }
    );
  }
}
