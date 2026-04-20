import { Database, Shield, BarChart3, Layers, FileSearch, Zap, BookOpen, ArrowRight } from 'lucide-react'
import UploadForm from '@/components/UploadForm'
import RecentSessions from '@/components/RecentSessions'

const TESTS = [
  { icon: FileSearch, name: 'Duplicate Detection',       desc: 'Fingerprint-based hashing to identify exact duplicate entries that inflate dataset size.' },
  { icon: BarChart3,  name: 'Category Distribution',     desc: 'Long-tail analysis to identify underrepresented categories that compromise statistical reliability.' },
  { icon: Layers,     name: 'Category Co-occurrence',    desc: 'Pearson correlation matrix to detect semantically redundant label pairs (r > 0.8).' },
  { icon: Shield,     name: 'Refusal Artifact Detection',desc: 'Lexical scan for 15 AI safety refusal patterns that create proxy shortcuts for classifiers.' },
  { icon: BookOpen,   name: 'Lexical Diversity',         desc: 'LDA topic modeling + normalized Shannon entropy to quantify thematic coverage.' },
  { icon: Zap,        name: 'Explanation Consistency',   desc: 'TF-IDF cosine similarity to detect circular reasoning in generated explanations.' },
  { icon: Database,   name: 'Severity Validation',       desc: 'Kolmogorov–Smirnov test to verify severity scores exhibit meaningful structure.' },
  { icon: BarChart3,  name: 'Class Balance & Coupling',  desc: 'Imbalance ratio analysis and category–class exclusivity detection for overfitting risk.' },
]

export default function HomePage() {
  return (
    <>
      {/* Hero */}
      <section className="bg-gray-900 text-white py-20 px-4">
        <div className="max-w-4xl mx-auto text-center">
          <div className="inline-flex items-center gap-2 bg-indigo-900/60 border border-indigo-700 rounded-full px-4 py-1.5 text-sm text-indigo-300 mb-6">
            <BookOpen className="w-4 h-4" />
            Based on peer-reviewed research &mdash; AI Ethics 2026
          </div>
          <h1 className="text-5xl font-bold mb-4 leading-tight">
            Automated Quality Audit for<br />
            <span className="text-indigo-400">AI Ethics Datasets</span>
          </h1>
          <p className="text-gray-400 text-lg max-w-2xl mx-auto mb-8">
            Upload any synthetic ethics dataset and receive a comprehensive structural audit across
            8 quality dimensions. Expose hidden weaknesses that performance metrics alone cannot reveal.
          </p>
          <div className="flex items-center justify-center gap-4 text-sm text-gray-500">
            <span className="flex items-center gap-1.5"><span className="w-2 h-2 rounded-full bg-green-400 inline-block" />Fully automated</span>
            <span className="flex items-center gap-1.5"><span className="w-2 h-2 rounded-full bg-indigo-400 inline-block" />8 diagnostic tests</span>
            <span className="flex items-center gap-1.5"><span className="w-2 h-2 rounded-full bg-amber-400 inline-block" />Composite quality score</span>
          </div>
        </div>
      </section>

      {/* Upload */}
      <section className="py-16 px-4 bg-white border-b border-gray-100" id="upload">
        <div className="max-w-2xl mx-auto">
          <h2 className="text-2xl font-bold text-gray-900 text-center mb-2">Audit Your Dataset</h2>
          <p className="text-gray-500 text-center mb-8">Upload a CSV, JSON, or JSONL file to run the full quality audit pipeline.</p>
          <UploadForm />
        </div>
      </section>

      {/* 8 Tests Grid */}
      <section className="py-16 px-4 bg-slate-50">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-3">8-Dimensional Audit Framework</h2>
            <p className="text-gray-500 max-w-2xl mx-auto">
              Each test targets a specific and documented failure mode in synthetic data generation,
              grounded in peer-reviewed literature with justified thresholds.
            </p>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
            {TESTS.map((t, i) => (
              <div key={t.name} className="bg-white rounded-xl border border-gray-200 p-5 hover:shadow-md transition-shadow">
                <div className="flex items-start gap-3 mb-3">
                  <div className="w-9 h-9 rounded-lg bg-indigo-100 flex items-center justify-center flex-shrink-0">
                    <t.icon className="w-5 h-5 text-indigo-600" />
                  </div>
                  <span className="text-xs font-mono text-indigo-400 font-semibold mt-1">T{i + 1}</span>
                </div>
                <h3 className="font-semibold text-gray-900 mb-1 text-sm">{t.name}</h3>
                <p className="text-xs text-gray-500 leading-relaxed">{t.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How it works */}
      <section className="py-16 px-4 bg-white border-t border-gray-100">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl font-bold text-gray-900 text-center mb-12">How It Works</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {[
              { step: '01', title: 'Upload Dataset', desc: 'Upload your CSV, JSON, or JSONL file. The framework auto-detects semantic columns — text, labels, categories, severity scores, and explanations.' },
              { step: '02', title: 'Run 8 Tests', desc: 'Eight independent diagnostic tests execute automatically, each targeting a specific failure mode documented in prior literature.' },
              { step: '03', title: 'Review Audit', desc: 'Get a composite quality score (0–100), per-test scores, visualizations, metrics, and targeted recommendations for improvement.' },
            ].map(item => (
              <div key={item.step} className="flex gap-4">
                <div className="w-12 h-12 rounded-xl bg-indigo-600 text-white flex items-center justify-center font-bold text-lg flex-shrink-0">{item.step}</div>
                <div>
                  <h3 className="font-semibold text-gray-900 mb-1">{item.title}</h3>
                  <p className="text-sm text-gray-500">{item.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Research context */}
      <section className="py-16 px-4 bg-gray-900 text-white">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl font-bold mb-4">Research Background</h2>
          <p className="text-gray-400 mb-6 leading-relaxed">
            This framework was developed as part of a study auditing the EthicsLens dataset — 38,813 synthetic
            samples spanning 163 ethical categories. The audit revealed a structural paradox: despite exceptional
            lexical diversity (H<sub>norm</sub> = 0.998) and strong category independence, the dataset contained
            33.58% duplicate entries and 90.18% of categories with fewer than 10 samples.
          </p>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
            {[
              { value: '76.2/100', label: 'EthicsLens Score' },
              { value: '33.58%', label: 'Duplicate Rate' },
              { value: '90.18%', label: 'Rare Categories' },
              { value: '0.998', label: 'Diversity Entropy' },
            ].map(s => (
              <div key={s.label} className="bg-gray-800 rounded-xl p-4 text-center">
                <p className="text-2xl font-bold text-indigo-400">{s.value}</p>
                <p className="text-xs text-gray-400 mt-1">{s.label}</p>
              </div>
            ))}
          </div>
          <a
            href="https://doi.org/10.1007/s43681-025-00904-4"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white px-5 py-2.5 rounded-xl text-sm font-medium transition-colors"
          >
            Read the Paper <ArrowRight className="w-4 h-4" />
          </a>
        </div>
      </section>

      {/* Recent sessions */}
      <section className="py-16 px-4 bg-slate-50 border-t border-gray-100">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Recent Audits</h2>
          <RecentSessions />
        </div>
      </section>
    </>
  )
}
