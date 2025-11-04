import { useEffect, useState } from 'react';
import { useScrollAnimation } from '@/hooks/use-scroll-animation';
import Navigation from '@/components/Navigation';
import Hero from '@/components/Hero';
import OurStory from '@/components/OurStory';
import SmokeDivider from '@/components/SmokeDivider';
import MenuCarousel from '@/components/MenuCarousel';
import OurValues from '@/components/OurValues';
import Testimonials from '@/components/Testimonials';
import QuoteCalculator from '@/components/QuoteCalculator';
import Locations from '@/components/Locations';
import Footer from '@/components/Footer';
import ChatBot from '@/components/ChatBot';

const Index = () => {
  const { ref, isVisible } = useScrollAnimation();

  return (
    <div className="min-h-screen bg-cream-white relative">
      <Navigation />

      {/* 1. Quote Calculator Section - FIRST */}
      <section className="min-h-screen flex items-center justify-center py-32 px-6 bg-gradient-to-br from-burnt-umber/10 via-cream-white to-faded-mustard/5 relative" id="calculator">
        <div className="absolute inset-0 overflow-hidden pointer-events-none opacity-10">
          <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-burnt-umber/30 rounded-full blur-[120px]" />
          <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-faded-mustard/20 rounded-full blur-[120px]" />
        </div>

        <div className="w-full max-w-3xl mx-auto relative z-10">
          <div
            ref={ref}
            className={`rounded shadow-card overflow-hidden transition-all duration-700 ease-out ${
              isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'
            }`}
          >
            <div className="bg-gradient-to-br from-amber-700 via-amber-600 to-yellow-700 text-faded-mustard p-12 text-center relative">
              <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-24 h-0.5 bg-faded-mustard/40" />
              <h1 className="text-4xl md:text-5xl tracking-[0.15em] uppercase mb-4 font-serif">
                Plan Your Feast
              </h1>
              <p className="text-base text-faded-mustard/90 tracking-wide font-light">
                Tell us about your gathering — we'll bring the fire
              </p>
            </div>

            <div className="p-12 bg-gradient-to-b from-cream-white/95 via-cream-white/75 to-cream-white/50 backdrop-blur-[2px]">
              <QuoteCalculator />
            </div>
          </div>
        </div>
      </section>

      {/* Smoke Line Divider */}
      <SmokeDivider />

      {/* 2. Testimonials - Stories from the Table - SECOND */}
      <Testimonials />

      {/* Smoke Line Divider */}
      <SmokeDivider />

      {/* 3. Menu Carousel - THIRD */}
      <MenuCarousel />

      {/* Smoke Line Divider */}
      <SmokeDivider />

      {/* 4. Our Values Section - FOURTH */}
      <OurValues />

      {/* Smoke Line Divider */}
      <SmokeDivider />

      {/* 5. Our Story Section - LAST */}
      <OurStory />

      {/* Hero Section - Moved to bottom as visual closer */}
      <Hero />

      {/* Footer */}
      <Footer />

      {/* ChatBot */}
      <ChatBot />
    </div>
  );
};

export default Index;
