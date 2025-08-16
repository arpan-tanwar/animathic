import { useState, useEffect } from "react";
import { Play, ArrowRight, Sparkles, Clock, Tag } from "lucide-react";
import { Link } from "react-router-dom";

export default function ExamplesPage() {
  const [mounted, setMounted] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState("all");

  useEffect(() => {
    setMounted(true);
  }, []);

  const categories = [
    { id: "all", name: "All Examples", count: 6 },
    { id: "calculus", name: "Calculus", count: 2 },
    { id: "algebra", name: "Algebra", count: 2 },
    { id: "geometry", name: "Geometry", count: 1 },
    { id: "statistics", name: "Statistics", count: 1 }
  ];

  const examples = [
    {
      id: 1,
      title: "Sine Wave from Unit Circle",
      category: "calculus",
      prompt: "Plot the graph of y = sin(x) from -2π to 2π showing how it emerges from the unit circle",
      videoUrl: "/examples/sin-graph.mp4",
      description: "Animated visualization connecting the unit circle to the sine function graph.",
      duration: "45s",
      complexity: "Beginner",
      tags: ["trigonometry", "functions", "unit circle"]
    },
    {
      id: 2,
      title: "Mathematical Text Animation",
      category: "algebra",
      prompt: "Show the text 'AI + Math = Magic' in the center with a writing effect",
      videoUrl: "/examples/text-reveal.mp4",
      description: "Elegant text animation using Manim's Write effect for smooth character-by-character reveal.",
      duration: "30s",
      complexity: "Beginner",
      tags: ["text", "animation", "effects"]
    },
    {
      id: 3,
      title: "Parabola Curve Tracing",
      category: "algebra",
      prompt: "Animate a dot moving along the curve y = x^2 from x = -3 to x = 3",
      videoUrl: "/examples/parabola-trace.mp4",
      description: "Dynamic visualization of quadratic function with animated point tracing the curve path.",
      duration: "60s",
      complexity: "Intermediate",
      tags: ["quadratic", "curve", "tracing"]
    },
    {
      id: 4,
      title: "Vector Addition Visualization",
      category: "geometry",
      prompt: "Visualize vector addition of (2,1) and (1,2) from the origin with arrow representations",
      videoUrl: "/examples/vector-addition.mp4",
      description: "Clear demonstration of vector addition using arrow graphics and coordinate system.",
      duration: "40s",
      complexity: "Intermediate",
      tags: ["vectors", "addition", "geometry"]
    },
    {
      id: 5,
      title: "Matrix Transformation",
      category: "algebra",
      prompt: "Apply a matrix transformation to a square to turn it into a parallelogram",
      videoUrl: "/examples/matrix-transform.mp4",
      description: "Linear algebra transformation visualized on a 2D grid showing shape deformation.",
      duration: "55s",
      complexity: "Advanced",
      tags: ["matrix", "transformation", "linear algebra"]
    },
    {
      id: 6,
      title: "Point Projection",
      category: "geometry",
      prompt: "Create a 2D graph and plot the points (-1, -1) and (1, 1), then draw dashed lines from each point down to their corresponding x-axis positions",
      videoUrl: "/examples/point-projection.mp4",
      description: "Geometric projection demonstration showing relationship between points and coordinate axes.",
      duration: "35s",
      complexity: "Beginner",
      tags: ["projection", "coordinates", "geometry"]
    }
  ];

  const filteredExamples = selectedCategory === "all" 
    ? examples 
    : examples.filter(example => example.category === selectedCategory);

  const getComplexityColor = (complexity: string) => {
    switch (complexity) {
      case "Beginner": return "text-green-400 bg-green-400/10";
      case "Intermediate": return "text-yellow-400 bg-yellow-400/10";
      case "Advanced": return "text-red-400 bg-red-400/10";
      default: return "text-secondary bg-surface-secondary";
    }
  };

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="pt-20 pb-12 lg:pt-28 lg:pb-16 relative">
        <div className="absolute inset-0 gradient-mesh opacity-30" />
        
        <div className="container-narrow relative">
          <div className="text-center space-y-6 max-w-3xl mx-auto">
            <h1 className={`text-4xl lg:text-5xl font-bold tracking-tight transition-all duration-700 ${mounted ? "animate-slide-up" : "opacity-0"}`}>
              Example <span className="text-gradient-primary">Animations</span>
            </h1>
            
            <p className={`text-lg text-secondary leading-relaxed transition-all duration-700 animate-delay-200 ${mounted ? "animate-slide-up" : "opacity-0"}`}>
              Explore these examples to see how Animathic transforms mathematical concepts 
              into engaging visual content. Each animation was created from a simple text prompt.
            </p>
          </div>
        </div>
      </section>

      {/* Category Filter */}
      <section className="pb-8">
        <div className="container-narrow">
          <div className={`transition-all duration-700 animate-delay-300 ${mounted ? "animate-fade-in" : "opacity-0"}`}>
            <div className="flex flex-wrap items-center justify-center gap-2">
              {categories.map((category) => (
                <button
                  key={category.id}
                  onClick={() => setSelectedCategory(category.id)}
                  className={`
                    px-4 py-2 rounded-xl text-sm font-medium transition-all duration-200 interactive focus-ring
                    ${selectedCategory === category.id
                      ? "bg-accent-primary text-white border border-accent-primary"
                      : "surface-secondary border border-subtle text-secondary hover:text-primary hover:border-emphasis"
                    }
                  `}
                >
                  {category.name}
                  <span className="ml-2 text-xs opacity-75">({category.count})</span>
                </button>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Examples Grid */}
      <section className="pb-16 lg:pb-24">
        <div className="container-narrow">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredExamples.map((example, index) => (
              <div
                key={example.id}
                className={`surface-primary rounded-2xl overflow-hidden border border-subtle interactive group transition-all duration-700 ${mounted ? "animate-scale-up" : "opacity-0"}`}
                style={{ animationDelay: `${(index + 4) * 100}ms` }}
              >
                {/* Video Preview */}
                <div className="aspect-video bg-surface-tertiary relative overflow-hidden">
                  <video
                    src={example.videoUrl}
                    poster={`${example.videoUrl.replace(".mp4", "-thumbnail.jpg")}`}
                    controls
                    className="w-full h-full object-contain bg-black/20"
                    preload="metadata"
                  />
                  
                  {/* Overlay badges */}
                  <div className="absolute top-3 left-3 flex items-center gap-2">
                    <span className="flex items-center gap-1 px-2 py-1 rounded-lg bg-black/60 text-white text-xs font-medium">
                      <Clock className="w-3 h-3" />
                      {example.duration}
                    </span>
                  </div>
                  
                  <div className="absolute top-3 right-3">
                    <span className={`px-2 py-1 rounded-lg text-xs font-medium ${getComplexityColor(example.complexity)}`}>
                      {example.complexity}
                    </span>
                  </div>
                </div>

                {/* Content */}
                <div className="p-5 space-y-4">
                  {/* Title and description */}
                  <div className="space-y-2">
                    <h3 className="text-lg font-semibold text-primary group-hover:text-accent-primary transition-colors duration-200">
                      {example.title}
                    </h3>
                    <p className="text-sm text-secondary leading-relaxed">
                      {example.description}
                    </p>
                  </div>

                  {/* Prompt */}
                  <div className="surface-secondary rounded-lg p-3 border border-subtle">
                    <p className="text-xs text-muted mb-1 font-medium">Original Prompt:</p>
                    <p className="text-sm text-primary font-medium leading-relaxed">
                      "{example.prompt}"
                    </p>
                  </div>

                  {/* Tags */}
                  <div className="flex flex-wrap gap-2">
                    {example.tags.map((tag, tagIndex) => (
                      <span
                        key={tagIndex}
                        className="inline-flex items-center gap-1 px-2 py-1 rounded-md bg-accent-primary/10 text-accent-primary text-xs font-medium"
                      >
                        <Tag className="w-3 h-3" />
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Empty state */}
          {filteredExamples.length === 0 && (
            <div className="text-center py-12">
              <p className="text-secondary">No examples found in this category.</p>
            </div>
          )}
        </div>
      </section>

      {/* Call to Action */}
      <section className="py-16 lg:py-24 bg-surface-primary/30">
        <div className="container-narrow">
          <div className="surface-primary rounded-3xl p-8 lg:p-12 text-center space-y-8">
            <div className="space-y-4">
              <div className="w-16 h-16 rounded-full bg-gradient-primary flex items-center justify-center mx-auto">
                <Sparkles className="w-8 h-8 text-white" />
              </div>
              
              <h2 className="text-3xl lg:text-4xl font-bold text-primary">
                Ready to Create Your Own?
              </h2>
              
              <p className="text-lg text-secondary max-w-2xl mx-auto">
                These examples were all created from simple text descriptions. 
                What mathematical concept would you like to bring to life?
              </p>
            </div>
            
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link
                to="/generate"
                className="btn-primary inline-flex items-center gap-2 interactive"
              >
                <Sparkles className="w-4 h-4" />
                <span>Start Creating</span>
                <ArrowRight className="w-4 h-4" />
              </Link>
              
              <Link
                to="/how-it-works"
                className="btn-ghost inline-flex items-center gap-2"
              >
                <span>Learn How It Works</span>
              </Link>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}