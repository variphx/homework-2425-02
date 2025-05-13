import { NextResponse } from "next/server";

export async function GET() {
  try {
    // Check if API URL is configured
    const hfSpaceUrl = process.env.NEXT_PUBLIC_HF_SPACE_URL;

    if (!hfSpaceUrl) {
      return NextResponse.json(
        {
          ok: false,
          message: "Hugging Face Space URL not configured",
        },
        { status: 200 }
      );
    }

    // Check if API token is configured - now server-side only
    const apiToken = process.env.HF_API_TOKEN;

    if (!apiToken) {
      return NextResponse.json(
        {
          ok: false,
          message: "API token not configured",
        },
        { status: 200 }
      );
    }

    // Try to connect to the Hugging Face Space
    try {
      const response = await fetch(`${hfSpaceUrl}/docs`);

      if (response.ok) {
        return NextResponse.json(
          {
            ok: true,
            message: "Hugging Face Space is available",
          },
          { status: 200 }
        );
      } else {
        return NextResponse.json(
          {
            ok: false,
            message: `Hugging Face Space returned status ${response.status}`,
          },
          { status: 200 }
        );
      }
    } catch (error) {
      return NextResponse.json(
        {
          ok: false,
          message: "Could not connect to Hugging Face Space",
        },
        { status: 200 }
      );
    }
  } catch (error) {
    console.error("Status check error:", error);
    return NextResponse.json(
      {
        ok: false,
        message: "Error checking API status",
      },
      { status: 200 }
    );
  }
}
