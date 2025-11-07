import { useScrollAnimation } from '@/hooks/use-scroll-animation';

const OurStory = () => {
  const { ref, isVisible } = useScrollAnimation();

  return (
    <section className="py-16 md:py-32 px-4 md:px-6 bg-cream-white relative overflow-hidden" id="about">
      {/* Linen texture background */}
      <div
        className="absolute inset-0 opacity-[0.03]"
        style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg width='100' height='100' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence baseFrequency='0.9' /%3E%3C/filter%3E%3Crect width='100' height='100' filter='url(%23noise)' opacity='0.4'/%3E%3C/svg%3E")`,
        }}
      />

      <div className="max-w-7xl mx-auto relative z-10">
        <div
          ref={ref}
          className={`grid md:grid-cols-2 gap-8 md:gap-16 items-center transition-all duration-1000 ${
            isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-12'
          }`}
        >
          {/* Left: Founder Image */}
          <div className="relative">
            <div className="aspect-[4/5] bg-gradient-to-br from-burnt-umber/20 to-charcoal-gray/20 rounded shadow-card overflow-hidden">
              {/* Placeholder for founder image */}
              <div className="w-full h-full flex items-center justify-center text-charcoal-gray/30">
                <svg
                  className="w-32 h-32"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={1}
                    d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"
                  />
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={1}
                    d="M15 13a3 3 0 11-6 0 3 3 0 016 0z"
                  />
                </svg>
              </div>
            </div>
            {/* Subtle frame effect */}
            <div className="absolute inset-0 border border-burnt-umber/10 rounded pointer-events-none" />
          </div>

          {/* Right: Story Text */}
          <div className="space-y-5 md:space-y-6">
            <div className="space-y-2">
              <p className="text-faded-mustard text-xs md:text-sm uppercase tracking-[0.2em] font-medium">
                It Started Around a Fire
              </p>
              <h2 className="text-3xl md:text-5xl font-serif text-charcoal-gray tracking-wide leading-tight">
                Our Story
              </h2>
            </div>

            <div className="w-16 h-0.5 bg-burnt-umber/30" />

            <blockquote className="text-lg md:text-2xl font-serif text-charcoal-gray/90 italic leading-relaxed border-l-2 border-faded-mustard pl-4 md:pl-6">
              "We believe BBQ should be slow, honest, and shared."
            </blockquote>

            <div className="space-y-3 md:space-y-4 text-charcoal-gray/70 leading-relaxed">
              <p>
                What began as weekend gatherings around the pit has grown into something deeper —
                a commitment to doing things right, no shortcuts, no compromises.
              </p>
              <p>
                Every brisket smoked for 14 hours. Every sauce stirred by hand.
                Every event treated like family coming home.
              </p>
              <p className="text-sm">
                <span className="text-burnt-umber font-medium">Family Owned</span> •
                <span className="text-burnt-umber font-medium ml-3">Post Oak Smoked</span> •
                <span className="text-burnt-umber font-medium ml-3">Since 2012</span>
              </p>
            </div>

            {/* Handwritten signature effect */}
            <div className="pt-4 md:pt-6">
              <div className="font-accent text-2xl md:text-3xl text-burnt-umber opacity-60">
                The Smokehouse Team
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default OurStory;
