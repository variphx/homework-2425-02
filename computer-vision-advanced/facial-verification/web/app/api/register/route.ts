import { type NextRequest, NextResponse } from "next/server";

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData();
    const image = formData.get("image") as File;
    const name = formData.get("name") as string;

    if (!image || !name) {
      return NextResponse.json(
        { error: "Missing required fields" },
        { status: 400 }
      );
    }

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
    apiFormData.append("image", image);
    apiFormData.append("name", name);

    console.log(
      `Sending registration request to ${hfSpaceUrl}/register for ${name}`
    );

    // Call the Hugging Face Space API
    const response = await fetch(`${hfSpaceUrl}/register`, {
      method: "POST",
      body: apiFormData,
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error(`Hugging Face API error (${response.status}):`, errorText);
      return NextResponse.json(
        { error: `API error: ${response.status}` },
        { status: response.status }
      );
    }

    const result = await response.json();
    console.log("Registration result:", result);

    if (result.status === "ok") {
      return NextResponse.json({
        status: "ok",
        message: "Face registered successfully",
      });
    } else {
      return NextResponse.json(
        { error: "Registration failed" },
        { status: 400 }
      );
    }
  } catch (error) {
    console.error("Registration error:", error);
    return NextResponse.json(
      { error: "Failed to process registration" },
      { status: 500 }
    );
  }
}
