import React from 'react';
import { PageTransition } from '../components/ui/PageTransition';

export default function Insights() {
  return (
    <PageTransition>
      <div className="flex flex-col gap-6">
        <div>
          <h1 className="text-3xl font-display font-medium text-astra-black tracking-tight">Insights</h1>
          <p className="text-text-secondary mt-1">Module under construction.</p>
        </div>
      </div>
    </PageTransition>
  );
}
