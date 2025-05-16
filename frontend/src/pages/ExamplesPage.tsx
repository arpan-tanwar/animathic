import { useState, useEffect } from "react";

export default function ExamplesPage() {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  const examples = [
    {
      title: "Function Plotting",
      prompt: "Plot the graph of y = sin(x) from -2π to 2π",
      videoUrl: "/examples/sin-graph.mp4",
      description: "Animated graph of the sine function with x and y axes.",
    },
    {
      title: "Text Reveal",
      prompt:
        "Show the text 'AI + Math = Magic' in the center with a writing effect",
      videoUrl: "/examples/text-reveal.mp4",
      description:
        "Text animation using Manim's Write effect for smooth entry.",
    },
    {
      title: "Parabola Curve Trace",
      prompt: "Animate a dot moving along the curve y = x^2",
      videoUrl: "/examples/parabola-trace.mp4",
      description: "A dot traces the path of a parabola with dynamic motion.",
    },
    {
      title: "Vector Addition",
      prompt: "Visualize vector addition of (2,1) and (1,2) from the origin",
      videoUrl: "/examples/vector-addition.mp4",
      description: "Arrow-based vector addition on x and y axes with labels.",
    },
    {
      title: "Matrix Transformation",
      prompt:
        "Apply a matrix transformation to a square to turn it into a parallelogram",
      videoUrl: "/examples/matrix-transform.mp4",
      description: "Linear algebra transformation visualized on a 2D grid.",
    },
    {
      title: "Point Projection on X-Axis",
      prompt:
        "Create a 2D graph and plot the points (-1, -1) and (1, 1), then draw dashed lines from each point down to their corresponding x-axis positions.",
      videoUrl: "/examples/point-projection.mp4",
      description:
        "Plots two points and visually connects them to the x-axis using vertical projections.",
    },
  ];

  return (
    <main className="flex flex-col items-center min-h-[calc(100vh-4rem)]">
      <div className="container max-w-6xl mx-auto py-8 px-4 sm:py-12 sm:px-6 lg:px-8">
        <div className="text-center space-y-4 mb-8">
          <h1
            className={`text-3xl font-bold tracking-tight sm:text-4xl transition-all duration-700 ${
              mounted ? "opacity-100 transform-none" : "opacity-0 translate-y-4"
            }`}
          >
            Example Animations
          </h1>
          <p
            className={`text-base text-muted-foreground max-w-2xl mx-auto transition-all duration-700 delay-100 ${
              mounted ? "opacity-100 transform-none" : "opacity-0 translate-y-4"
            }`}
          >
            Explore these examples to see how Animathic transforms mathematical
            ideas into beautiful animations.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {examples.map((example, index) => (
            <div
              key={index}
              className={`bg-card rounded-lg overflow-hidden shadow-lg transition-all duration-700 ${
                mounted
                  ? "opacity-100 transform-none"
                  : "opacity-0 translate-y-4"
              }`}
              style={{ transitionDelay: `${(index + 2) * 100}ms` }}
            >
              <div className="aspect-video bg-black">
                <video
                  src={example.videoUrl}
                  poster={`${example.videoUrl.replace(
                    ".mp4",
                    "-thumbnail.jpg"
                  )}`}
                  controls
                  className="w-full h-full object-contain"
                />
              </div>
              <div className="p-4">
                <h2 className="text-xl font-semibold mb-2">{example.title}</h2>
                <p className="text-sm text-muted-foreground mb-3">
                  {example.prompt}
                </p>
                <div className="text-xs bg-accent/50 p-2 rounded-md">
                  <span className="font-medium text-muted-foreground">
                    Description:{" "}
                  </span>
                  {example.description}
                </div>
              </div>
            </div>
          ))}
        </div>

        <div
          className={`mt-8 p-4 rounded-lg bg-accent/50 transition-all duration-700 delay-700 ${
            mounted ? "opacity-100 transform-none" : "opacity-0 translate-y-4"
          }`}
        >
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
            <div>
              <h3 className="text-lg font-semibold mb-1">Try It Yourself</h3>
              <p className="text-sm text-muted-foreground">
                Create your own mathematical animations with our AI-powered
                generator.
              </p>
            </div>
            <a
              href="/"
              className="inline-flex items-center justify-center rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-9 px-4"
            >
              Start Creating
            </a>
          </div>
        </div>
      </div>
    </main>
  );
}
