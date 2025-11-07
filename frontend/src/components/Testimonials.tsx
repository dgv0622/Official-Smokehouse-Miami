import { useState, useEffect } from 'react';
import { useScrollAnimation } from '@/hooks/use-scroll-animation';

const testimonials = [
  {
    quote: "The brisket literally melted in our mouths. Our wedding guests are still talking about it six months later.",
    author: "Sarah & Michael",
    event: "Wedding Reception",
    initials: "S&M"
  },
  {
    quote: "Professional, punctual, and the food was absolutely incredible. Made our corporate event feel like a family gathering.",
    author: "David Rodriguez",
    event: "Corporate Event",
    initials: "DR"
  },
  {
    quote: "Real BBQ from real people. You can taste the care in every bite. This is how food should be.",
    author: "The Martinez Family",
    event: "Family Reunion",
    initials: "TM"
  },
  {
    quote: "We've used them three times now. The consistency, the flavor, the service — everything is just perfect.",
    author: "Jennifer Parks",
    event: "Private Party",
    initials: "JP"
  },
];

const Testimonials = () => {
  const { ref, isVisible } = useScrollAnimation();
  const [currentIndex, setCurrentIndex] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentIndex((prev) => (prev + 1) % testimonials.length);
    }, 4000);

    return () => clearInterval(interval);
  }, []);

  return (
    <section className="py-16 md:py-32 px-4 md:px-6 bg-gradient-to-b from-burnt-umber/5 to-cream-white">
      <div className="max-w-4xl mx-auto">
        {/* Section Header */}
        <div
          ref={ref}
          className={`text-center mb-10 md:mb-16 transition-all duration-1000 ${
            isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-12'
          }`}
        >
          <p className="text-faded-mustard text-xs md:text-sm uppercase tracking-[0.2em] font-medium mb-2">
            Stories from the Table
          </p>
          <h2 className="text-3xl md:text-5xl font-serif text-charcoal-gray tracking-wide">
            What Folks Say
          </h2>
        </div>

        {/* Testimonial Display */}
        <div className="relative min-h-[280px] md:min-h-[300px] flex items-center justify-center">
          {testimonials.map((testimonial, index) => (
            <div
              key={index}
              className={`absolute inset-0 flex flex-col items-center justify-center text-center px-4 md:px-6 transition-opacity duration-700 ${
                index === currentIndex ? 'opacity-100' : 'opacity-0 pointer-events-none'
              }`}
            >
              {/* Circle with initials */}
              <div className="w-16 h-16 md:w-20 md:h-20 rounded-full bg-gradient-to-br from-burnt-umber to-dusty-red flex items-center justify-center text-cream-white text-lg md:text-xl font-serif mb-6 md:mb-8 shadow-soft">
                {testimonial.initials}
              </div>

              {/* Quote */}
              <blockquote className="text-xl md:text-3xl font-serif text-charcoal-gray italic leading-relaxed mb-4 md:mb-6">
                "{testimonial.quote}"
              </blockquote>

              {/* Author */}
              <div className="space-y-1">
                <p className="text-burnt-umber font-medium">{testimonial.author}</p>
                <p className="text-charcoal-gray/60 text-sm">{testimonial.event}</p>
              </div>
            </div>
          ))}
        </div>

        {/* Dots */}
        <div className="flex justify-center gap-2 mt-8 md:mt-12">
          {testimonials.map((_, index) => (
            <button
              key={index}
              onClick={() => setCurrentIndex(index)}
              className={`w-2 h-2 rounded-full transition-all duration-300 ${
                index === currentIndex
                  ? 'bg-burnt-umber w-8'
                  : 'bg-burnt-umber/30 hover:bg-burnt-umber/50'
              }`}
              aria-label={`View testimonial ${index + 1}`}
            />
          ))}
        </div>
      </div>
    </section>
  );
};

export default Testimonials;