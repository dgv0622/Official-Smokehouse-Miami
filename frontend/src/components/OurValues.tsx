import { useScrollAnimation } from '@/hooks/use-scroll-animation';

const values = [
  {
    title: 'Honest Craft',
    description: 'No shortcuts. No compromises. Just real wood, real time, real technique.',
  },
  {
    title: 'Family First',
    description: 'Every event is treated like our own family gathering. Your celebration matters.',
  },
  {
    title: 'Community Roots',
    description: 'Sourcing local. Supporting neighbors. Building something bigger than BBQ.',
  },
];

const OurValues = () => {
  const { ref, isVisible } = useScrollAnimation();

  return (
    <section className="py-16 md:py-32 relative overflow-hidden">
      {/* Background image area (right side) */}
      <div className="absolute right-0 top-0 bottom-0 w-1/2 bg-gradient-to-l from-burnt-umber/10 to-transparent" />

      {/* Linen texture overlay */}
      <div
        className="absolute inset-0 opacity-[0.04] mix-blend-multiply"
        style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence baseFrequency='0.65' /%3E%3C/filter%3E%3Crect width='60' height='60' filter='url(%23noise)'/%3E%3C/svg%3E")`,
        }}
      />

      <div className="max-w-7xl mx-auto px-4 md:px-6 relative z-10">
        <div
          ref={ref}
          className={`grid md:grid-cols-2 gap-8 md:gap-16 items-center transition-all duration-1000 ${
            isVisible ? 'opacity-100 translate-x-0' : 'opacity-0 -translate-x-12'
          }`}
        >
          {/* Left: Values Text */}
          <div className="space-y-6 md:space-y-8">
            <div>
              <p className="text-faded-mustard text-xs md:text-sm uppercase tracking-[0.2em] font-medium mb-2">
                What We Stand For
              </p>
              <h2 className="text-3xl md:text-5xl font-serif text-charcoal-gray tracking-wide leading-tight">
                Our Values
              </h2>
            </div>

            <div className="w-16 h-0.5 bg-burnt-umber/30" />

            <div className="space-y-6 md:space-y-8">
              {values.map((value, index) => (
                <div
                  key={value.title}
                  className="space-y-2 animate-in fade-in-up duration-700"
                  style={{ animationDelay: `${index * 150}ms`, animationFillMode: 'backwards' }}
                >
                  <h3 className="text-lg md:text-xl font-serif text-burnt-umber">{value.title}</h3>
                  <p className="text-charcoal-gray/70 leading-relaxed">
                    {value.description}
                  </p>
                </div>
              ))}
            </div>

            <div className="pt-3 md:pt-4">
              <p className="text-sm text-charcoal-gray/60 italic">
                "Patience, craftsmanship, and community —
                <br />
                these are the pillars of everything we smoke."
              </p>
            </div>
          </div>

          {/* Right: Background photo placeholder */}
          <div className="relative">
            <div className="aspect-[3/4] bg-gradient-to-br from-burnt-umber/20 to-charcoal-gray/20 rounded shadow-card overflow-hidden">
              {/* Placeholder for hands slicing brisket */}
              <div className="w-full h-full flex items-center justify-center">
                <div className="text-charcoal-gray/20 text-center">
                  <svg 
                    className="w-32 h-32 mx-auto mb-4" 
                    fill="none" 
                    stroke="currentColor" 
                    viewBox="0 0 24 24"
                  >
                    <path 
                      strokeLinecap="round" 
                      strokeLinejoin="round" 
                      strokeWidth={1} 
                      d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" 
                    />
                  </svg>
                  <p className="text-sm">Image: Hands slicing brisket</p>
                </div>
              </div>
            </div>
            <div className="absolute inset-0 border border-burnt-umber/10 rounded pointer-events-none" />
          </div>
        </div>
      </div>
    </section>
  );
};

export default OurValues;